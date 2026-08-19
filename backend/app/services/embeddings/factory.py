"""Select the configured embedding provider without leaking provider details upstream."""

from app.core.config import settings
from app.services.embeddings.base_provider import EmbeddingError
from app.services.embeddings.base_provider import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    provider_name = settings.RAG_EMBEDDING_PROVIDER.strip().lower()

    if provider_name == "openai":
        from app.services.embeddings.openai_provider import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider()

    if provider_name == "local":
        from app.services.embeddings.local_provider import LocalEmbeddingProvider

        return LocalEmbeddingProvider()

    raise EmbeddingError("Unsupported RAG embedding provider configuration.")
