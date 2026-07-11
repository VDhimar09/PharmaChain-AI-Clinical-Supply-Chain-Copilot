from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATABASE_URL: str

    JWT_SECRET_KEY: str = "change-me-in-production"

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    JWT_ISSUER: str = "pharmachain-api"

    BOOTSTRAP_ADMIN_EMAIL: str = "admin@pharmachain.com"

    BOOTSTRAP_ADMIN_PASSWORD: str = "ChangeMe123!"

    BOOTSTRAP_ADMIN_NAME: str = "PharmaChain Administrator"

    OPENAI_API_KEY: str | None = None

    AZURE_OPENAI_ENDPOINT: str | None = None

    AZURE_OPENAI_API_KEY: str | None = None

    class Config:

        env_file = ".env"


settings = Settings()
