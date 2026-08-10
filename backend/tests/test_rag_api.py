from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.rag import router as rag_router
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.services.rag_generation_service import (
    Citation,
    RagGenerationError,
    RagQueryResult,
)
from app.services.retriever_service import RetrievalResult


DOCUMENT_ID = uuid4()
CHUNK_ID = uuid4()

FAKE_RESULTS = [
    RetrievalResult(
        document_id=DOCUMENT_ID,
        chunk_id=CHUNK_ID,
        filename="Cold_Chain_SOP.pdf",
        page_number=12,
        content="Temperature excursions must be logged within one hour.",
        similarity=0.89,
    )
]


def _create_app(permissions: list[str]) -> FastAPI:
    app = FastAPI()
    app.include_router(rag_router)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        email="user@example.com",
        full_name="Test User",
        role=SimpleNamespace(
            name="Tester",
            permissions=[
                SimpleNamespace(name=permission)
                for permission in permissions
            ],
        ),
    )
    return app


@pytest.fixture
def client_factory():
    def factory(permissions: list[str]) -> TestClient:
        return TestClient(_create_app(permissions))

    return factory


def test_search_requires_rag_search_permission(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.retriever_service.RetrieverService.search",
        lambda self, query: FAKE_RESULTS,
    )
    payload = {"query": "What does the cold-chain SOP say about temperature excursions?"}

    allowed = client_factory(["rag.search"]).post("/api/rag/search", json=payload)
    denied = client_factory([]).post("/api/rag/search", json=payload)

    assert allowed.status_code == 200
    assert denied.status_code == 403


def test_search_returns_evidence_with_citations(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.retriever_service.RetrieverService.search",
        lambda self, query: FAKE_RESULTS,
    )
    payload = {"query": "temperature excursions"}

    response = client_factory(["rag.search"]).post("/api/rag/search", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["query"] == "temperature excursions"
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["document_id"] == str(DOCUMENT_ID)
    assert result["filename"] == "Cold_Chain_SOP.pdf"
    assert result["page_number"] == 12
    assert result["similarity"] == pytest.approx(0.89)
    # Evidence only - no LLM-generated answer field should be present.
    assert "answer" not in body


def test_search_with_no_relevant_results_returns_empty_list(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.retriever_service.RetrieverService.search",
        lambda self, query: [],
    )

    response = client_factory(["rag.search"]).post(
        "/api/rag/search",
        json={"query": "completely unrelated nonsense query"},
    )

    assert response.status_code == 200
    assert response.json()["results"] == []


def test_search_rejects_empty_query(client_factory):
    response = client_factory(["rag.search"]).post(
        "/api/rag/search", json={"query": ""}
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/rag/query
# ---------------------------------------------------------------------------

GROUNDED_RESULT = RagQueryResult(
    answer="Temperature excursions must be logged within one hour.",
    grounded=True,
    citations=[
        Citation(
            document_id=DOCUMENT_ID,
            filename="Cold_Chain_SOP.pdf",
            page_number=12,
        )
    ],
)

UNGROUNDED_RESULT = RagQueryResult(
    answer="I couldn't find that information in the uploaded documentation.",
    grounded=False,
    citations=[],
)


def test_query_requires_rag_query_permission(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.api.rag.RagGenerationService.query",
        lambda self, query: GROUNDED_RESULT,
    )
    payload = {"query": "What does the cold-chain SOP say about temperature excursions?"}

    allowed = client_factory(["rag.query"]).post("/api/rag/query", json=payload)
    denied = client_factory([]).post("/api/rag/query", json=payload)

    assert allowed.status_code == 200
    assert denied.status_code == 403


def test_query_requires_authentication():
    app = FastAPI()
    app.include_router(rag_router)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    client = TestClient(app)

    response = client.post(
        "/api/rag/query",
        json={"query": "temperature excursions"},
    )

    assert response.status_code == 401


def test_query_rejects_empty_query(client_factory):
    response = client_factory(["rag.query"]).post(
        "/api/rag/query", json={"query": ""}
    )

    assert response.status_code == 422


def test_query_returns_grounded_answer_with_citations(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.api.rag.RagGenerationService.query",
        lambda self, query: GROUNDED_RESULT,
    )

    response = client_factory(["rag.query"]).post(
        "/api/rag/query",
        json={"query": "What does the cold-chain SOP say about temperature excursions?"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["grounded"] is True
    assert body["answer"] == GROUNDED_RESULT.answer
    assert len(body["citations"]) == 1
    assert body["citations"][0]["document_id"] == str(DOCUMENT_ID)
    assert body["citations"][0]["filename"] == "Cold_Chain_SOP.pdf"
    assert body["citations"][0]["page_number"] == 12


def test_query_with_no_evidence_returns_ungrounded_fallback(client_factory, monkeypatch):
    monkeypatch.setattr(
        "app.api.rag.RagGenerationService.query",
        lambda self, query: UNGROUNDED_RESULT,
    )

    response = client_factory(["rag.query"]).post(
        "/api/rag/query",
        json={"query": "completely unrelated nonsense query"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["grounded"] is False
    assert body["citations"] == []
    assert body["answer"] == UNGROUNDED_RESULT.answer


def test_query_returns_503_when_llm_generation_fails(client_factory, monkeypatch):
    def _raise(self, query):
        raise RagGenerationError("Failed to generate a grounded answer.")

    monkeypatch.setattr(
        "app.api.rag.RagGenerationService.query",
        _raise,
    )

    response = client_factory(["rag.query"]).post(
        "/api/rag/query",
        json={"query": "What does the cold-chain SOP say?"},
    )

    assert response.status_code == 503
