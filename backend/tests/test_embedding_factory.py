import pytest

from app.core.config import settings
from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.factory import get_embedding_provider


def test_factory_selects_local_provider(monkeypatch):
    class LocalProvider:
        profile = "local"

    monkeypatch.setattr(settings, "RAG_EMBEDDING_PROVIDER", "local")
    monkeypatch.setattr(
        "app.services.embeddings.local_provider.LocalEmbeddingProvider",
        LocalProvider,
    )

    assert get_embedding_provider().profile == "local"


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(settings, "RAG_EMBEDDING_PROVIDER", "unsupported")

    with pytest.raises(EmbeddingError):
        get_embedding_provider()
