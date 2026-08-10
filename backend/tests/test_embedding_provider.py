import pytest
from openai import APIConnectionError

from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.openai_provider import OpenAIEmbeddingProvider
from tests.fakes import FakeEmbeddingProvider


def test_fake_provider_is_deterministic():
    provider = FakeEmbeddingProvider(dimension=16)

    first = provider.embed_text("cold chain temperature excursion")
    second = provider.embed_text("cold chain temperature excursion")

    assert first == second


def test_fake_provider_reports_configured_dimension():
    provider = FakeEmbeddingProvider(dimension=32)

    vector = provider.embed_text("anything")

    assert provider.dimension == 32
    assert len(vector) == 32


def test_fake_provider_preserves_batch_order():
    provider = FakeEmbeddingProvider(dimension=8)

    texts = ["alpha", "beta", "gamma"]
    vectors = provider.embed_texts(texts)

    assert len(vectors) == 3
    assert vectors[0] == provider.embed_text("alpha")
    assert vectors[2] == provider.embed_text("gamma")


def test_fake_provider_similar_texts_are_closer_than_dissimilar_ones():
    provider = FakeEmbeddingProvider(dimension=32)

    def cosine(a, b):
        return sum(x * y for x, y in zip(a, b))

    base = provider.embed_text("cold chain temperature excursion sop")
    similar = provider.embed_text("cold chain temperature excursion policy")
    unrelated = provider.embed_text("quarterly procurement budget review")

    assert cosine(base, similar) > cosine(base, unrelated)


def test_fake_provider_raises_embedding_error_when_configured_to_fail():
    provider = FakeEmbeddingProvider(dimension=8, fail_on={"boom"})

    with pytest.raises(EmbeddingError):
        provider.embed_text("boom")


def test_openai_provider_requires_api_key():
    with pytest.raises(EmbeddingError):
        OpenAIEmbeddingProvider(api_key="")


def test_openai_provider_returns_embeddings_in_request_order(monkeypatch):
    captured_kwargs = {}

    class _FakeEmbeddingItem:
        def __init__(self, index, embedding):
            self.index = index
            self.embedding = embedding

    class _FakeResponse:
        def __init__(self, items):
            self.data = items

    class _FakeEmbeddingsResource:
        def create(self, model, input, dimensions):
            captured_kwargs.update(
                {"model": model, "input": input, "dimensions": dimensions}
            )
            # Return out of order to prove the provider re-sorts by index.
            return _FakeResponse(
                [
                    _FakeEmbeddingItem(1, [0.2, 0.2]),
                    _FakeEmbeddingItem(0, [0.1, 0.1]),
                ]
            )

    class _FakeOpenAIClient:
        def __init__(self, api_key):
            self.embeddings = _FakeEmbeddingsResource()

    monkeypatch.setattr(
        "app.services.embeddings.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )

    provider = OpenAIEmbeddingProvider(
        model="text-embedding-3-small",
        dimension=2,
        api_key="fake-key",
    )

    result = provider.embed_texts(["first", "second"])

    assert result == [[0.1, 0.1], [0.2, 0.2]]
    assert captured_kwargs == {
        "model": "text-embedding-3-small",
        "input": ["first", "second"],
        "dimensions": 2,
    }


def test_openai_provider_wraps_provider_errors(monkeypatch):
    class _FailingEmbeddingsResource:
        def create(self, model, input, dimensions):
            raise APIConnectionError(request=None)

    class _FakeOpenAIClient:
        def __init__(self, api_key):
            self.embeddings = _FailingEmbeddingsResource()

    monkeypatch.setattr(
        "app.services.embeddings.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )

    provider = OpenAIEmbeddingProvider(api_key="fake-key", dimension=4)

    with pytest.raises(EmbeddingError):
        provider.embed_texts(["hello"])


def test_openai_provider_batches_large_requests(monkeypatch):
    batch_sizes = []

    class _FakeEmbeddingItem:
        def __init__(self, index, embedding):
            self.index = index
            self.embedding = embedding

    class _FakeResponse:
        def __init__(self, items):
            self.data = items

    class _FakeEmbeddingsResource:
        def create(self, model, input, dimensions):
            batch_sizes.append(len(input))
            return _FakeResponse(
                [
                    _FakeEmbeddingItem(i, [0.0])
                    for i in range(len(input))
                ]
            )

    class _FakeOpenAIClient:
        def __init__(self, api_key):
            self.embeddings = _FakeEmbeddingsResource()

    monkeypatch.setattr(
        "app.services.embeddings.openai_provider.OpenAI",
        _FakeOpenAIClient,
    )
    monkeypatch.setattr(
        "app.services.embeddings.openai_provider._BATCH_SIZE",
        3,
    )

    provider = OpenAIEmbeddingProvider(api_key="fake-key", dimension=1)
    result = provider.embed_texts([f"text-{i}" for i in range(7)])

    assert len(result) == 7
    assert batch_sizes == [3, 3, 1]
