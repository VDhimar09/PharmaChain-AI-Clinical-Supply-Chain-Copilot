from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # Database
    # ==========================================
    DATABASE_URL: str

    # ==========================================
    # JWT
    # ==========================================
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    JWT_ISSUER: str = "pharmachain-api"

    # ==========================================
    # Bootstrap Administrator
    # ==========================================
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@pharmachain.com"
    BOOTSTRAP_ADMIN_PASSWORD: str = "ChangeMe123!"
    BOOTSTRAP_ADMIN_NAME: str = "PharmaChain Administrator"

    # ==========================================
    # AI Providers
    # ==========================================
    OPENAI_API_KEY: str | None = None

    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None

    # ==========================================
    # RAG / Document Ingestion
    # ==========================================
    RAG_STORAGE_DIR: str = "storage/documents"

    RAG_MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    RAG_ALLOWED_MIME_TYPES: str = "application/pdf"
    RAG_ALLOWED_EXTENSIONS: str = ".pdf"

    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 150
    RAG_MIN_CHUNK_SIZE: int = 100

    RAG_EMBEDDING_PROVIDER: str = "openai"
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_EMBEDDING_DIMENSION: int = 1536

    RAG_SEARCH_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.5

    # ==========================================
    # CORS
    # ==========================================
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173"
    )

    # ==========================================
    # Environment
    # ==========================================
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()