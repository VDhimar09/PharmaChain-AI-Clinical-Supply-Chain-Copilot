from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.permission import Permission  # noqa: F401
from app.models.role import Role


class RoleRepository:

    @staticmethod
    def get_by_name(
        db: Session,
        role_name: str
    ) -> Role | None:
        return (
            db.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.name == role_name)
            .first()
        )

    @staticmethod
    def get_all(db: Session) -> list[Role]:
        return (
            db.query(Role)
            .options(joinedload(Role.permissions))
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        role: Role
    ) -> Role:
        db.add(role)
        db.flush()
        return role
