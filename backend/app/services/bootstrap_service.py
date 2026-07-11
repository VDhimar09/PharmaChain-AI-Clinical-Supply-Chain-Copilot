from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


ROLE_PERMISSIONS = {
    "Administrator": [
        ("system.admin", "Full platform administration"),

        ("inventory.read", "View inventory"),
        ("inventory.write", "Create and update inventory"),

        ("warehouse.read", "View warehouse"),
        ("warehouse.write", "Manage warehouse"),

        ("shipment.read", "View shipments"),
        ("shipment.write", "Manage shipments"),

        ("supplier.read", "View suppliers"),
        ("supplier.write", "Manage suppliers"),

        ("procurement.read", "View procurement"),
        ("procurement.write", "Create procurement"),
        ("procurement.approve", "Approve procurement"),

        ("insights.view", "View AI Insights"),
        ("copilot.use", "Use Executive Copilot"),
        ("audit.read", "View audit logs"),
        ("system.monitor", "Monitor background jobs"),
    ],

    "Operations Manager": [
        ("inventory.read", "View inventory"),
        ("warehouse.read", "View warehouse"),
        ("shipment.read", "View shipments"),
        ("procurement.read", "View procurement"),

        ("insights.view", "View AI Insights"),
        ("copilot.use", "Use Executive Copilot"),
    ],

    "Warehouse Manager": [
        ("inventory.read", "View inventory"),
        ("inventory.write", "Manage inventory"),

        ("warehouse.read", "View warehouse"),
        ("warehouse.write", "Manage warehouse"),

        ("shipment.read", "View shipments"),

        ("copilot.use", "Use Executive Copilot"),
    ],

    "Procurement Manager": [
        ("supplier.read", "View suppliers"),
        ("supplier.write", "Manage suppliers"),

        ("procurement.read", "View procurement"),
        ("procurement.write", "Manage procurement"),
        ("procurement.approve", "Approve procurement"),

        ("inventory.read", "View inventory"),

        ("insights.view", "View AI Insights"),
        ("copilot.use", "Use Executive Copilot"),
    ],

    "Viewer": [
        ("inventory.read", "View inventory"),
        ("warehouse.read", "View warehouse"),
        ("shipment.read", "View shipments"),
        ("supplier.read", "View suppliers"),
        ("procurement.read", "View procurement"),
        ("insights.view", "View AI Insights"),
    ],
}


class BootstrapService:

    @staticmethod
    def initialize_auth_data(db: Session) -> None:
        roles_by_name: dict[str, Role] = {}

        for role_name, permissions in ROLE_PERMISSIONS.items():

            role = RoleRepository.get_by_name(db, role_name)

            if role is None:
                role = Role(
                    name=role_name,
                    description=f"{role_name} role",
                )
                RoleRepository.create(db, role)

            existing_permissions = {
                permission.name
                for permission in role.permissions
            }

            for permission_name, description in permissions:

                if permission_name not in existing_permissions:
                    role.permissions.append(
                        Permission(
                            name=permission_name,
                            description=description,
                        )
                    )

            roles_by_name[role_name] = role

        admin_email = settings.BOOTSTRAP_ADMIN_EMAIL.lower()

        admin_user = UserRepository.get_by_email(
            db,
            admin_email,
        )

        if admin_user is None:
            UserRepository.create(
                db,
                User(
                    email=admin_email,
                    full_name=settings.BOOTSTRAP_ADMIN_NAME,
                    password_hash=hash_password(
                        settings.BOOTSTRAP_ADMIN_PASSWORD
                    ),
                    role=roles_by_name["Administrator"],
                    is_active=True,
                )
            )

        db.commit()
