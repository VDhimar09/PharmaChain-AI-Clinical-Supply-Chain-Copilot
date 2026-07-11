from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    @staticmethod
    def get_by_hash(
        db: Session,
        token_hash: str
    ) -> RefreshToken | None:
        return (
            db.query(RefreshToken)
            .options(joinedload(RefreshToken.user))
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        refresh_token: RefreshToken
    ) -> RefreshToken:
        db.add(refresh_token)
        db.flush()
        return refresh_token

    @staticmethod
    def revoke(
        db: Session,
        refresh_token: RefreshToken,
        revoked_at: datetime
    ) -> RefreshToken:
        refresh_token.revoked_at = revoked_at
        db.flush()
        return refresh_token
