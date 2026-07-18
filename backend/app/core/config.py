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