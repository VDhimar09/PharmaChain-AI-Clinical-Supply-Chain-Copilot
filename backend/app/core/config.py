from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATABASE_URL: str

    OPENAI_API_KEY: str | None = None

    AZURE_OPENAI_ENDPOINT: str | None = None

    AZURE_OPENAI_API_KEY: str | None = None

    class Config:

        env_file = ".env"


settings = Settings()