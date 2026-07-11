from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.core.config import settings
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.base import Base
from app.models.inventory import Inventory  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.procurement_request import ProcurementRequest  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.shipment import Shipment  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
from app.models.system_event import SystemEvent  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.warehouse_zone import WarehouseZone  # noqa: F401


config = context.config
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
