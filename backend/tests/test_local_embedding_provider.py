import pytest

from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.local_provider import LocalEmbeddingProvider


class FakeSentenceTransformer:
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.calls = []

    def get_sentence_embedding_dimension(self):
        return self.dimension

    def encode(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        return [[float(index + 1) for index in range(self.dimension)] for _ in texts]


def test_local_provider_reports_local_profile_and_dimension():
    provider = LocalEmbeddingProvider(model=FakeSentenceTransformer(), dimension=384)

    assert provider.profile == "local"
    assert provider.dimension == 384


def test_local_provider_returns_float_vectors_in_input_order():
    model = FakeSentenceTransformer(dimension=3)
    provider = LocalEmbeddingProvider(model=model, dimension=3)

    result = provider.embed_texts(["first", "second"])

    assert result == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    assert model.calls[0][0] == ["first", "second"]
    assert model.calls[0][1]["normalize_embeddings"] is True


def test_local_provider_is_deterministic_for_the_same_model_output():
    provider = LocalEmbeddingProvider(model=FakeSentenceTransformer(dimension=2), dimension=2)

    assert provider.embed_text("cold chain") == provider.embed_text("cold chain")


def test_local_provider_handles_empty_batch_and_rejects_empty_text():
    provider = LocalEmbeddingProvider(model=FakeSentenceTransformer(), dimension=384)

    assert provider.embed_texts([]) == []
    with pytest.raises(EmbeddingError):
        provider.embed_texts(["   "])


def test_local_provider_rejects_dimension_mismatch():
    with pytest.raises(EmbeddingError):
        LocalEmbeddingProvider(model=FakeSentenceTransformer(dimension=3), dimension=384)
