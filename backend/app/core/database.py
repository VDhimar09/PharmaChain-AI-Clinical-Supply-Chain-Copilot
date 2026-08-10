from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from app.core.config import settings


# SQL echo includes full statement parameters - now that RAG stores
# document chunk text and embedding vectors, that output must not reach
# logs outside local development. Any ENVIRONMENT value other than the
# "development" default (e.g. "production", "staging") disables it.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development"
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()