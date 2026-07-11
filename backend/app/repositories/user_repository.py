from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.permission import Permission  # noqa: F401
from app.models.role import Role
from app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.role).joinedload(Role.permissions)
            )
            .filter(User.email == email.lower())
            .first()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: UUID
    ) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.role).joinedload(Role.permissions)
            )
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        user: User
    ) -> User:
        db.add(user)
        db.flush()
        return user
