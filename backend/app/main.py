from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
import logging

from app.core.database import engine
from app.core.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.jobs.scheduler import get_scheduler_service

from app.models.base import Base
from app.models.audit_log import AuditLog
from app.models.system_event import SystemEvent
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.warehouse_zone import WarehouseZone
from app.models.inventory import Inventory
from app.models.shipment import Shipment
from app.models.procurement_request import ProcurementRequest
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.refresh_token import RefreshToken

from app.api.products import router as product_router
from app.api.suppliers import router as supplier_router
from app.api.inventory import router as inventory_router
from app.api.dashboard import router as dashboard_router
from app.api.warehouse_zone import router as warehouse_zone_router
from app.api.shipment import router as shipment_router
from app.api.procurement_request import (
    router as procurement_request_router
)
from app.api.procurement_ai import (
    router as procurement_ai_router
)
from app.api.ai import router as ai_router
from app.api.ai_chat import router as ai_chat_router
from app.api.audit import router as audit_router
from app.api.system_jobs import router as system_jobs_router
from app.api.auth import router as auth_router
from app.services.bootstrap_service import BootstrapService


logger = logging.getLogger(__name__)


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PharmaChain API",
    version="0.1.0"
)


@app.on_event("startup")
def initialize_application():
    db = SessionLocal()
    try:
        BootstrapService.initialize_auth_data(db)
    finally:
        db.close()

    try:
        scheduler_service = get_scheduler_service()
        scheduler_service.start()
        app.state.scheduler_service = scheduler_service
    except RuntimeError:
        logger.exception(
            "Background scheduler could not be started."
        )
        app.state.scheduler_service = None


@app.on_event("shutdown")
def shutdown_application():
    scheduler_service = getattr(
        app.state,
        "scheduler_service",
        None,
    )

    if scheduler_service is not None:
        scheduler_service.shutdown()

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Register Routers
# ----------------------------
protected_dependencies = [Depends(get_current_user)]

app.include_router(auth_router)
app.include_router(product_router, dependencies=protected_dependencies)
app.include_router(supplier_router, dependencies=protected_dependencies)
app.include_router(inventory_router, dependencies=protected_dependencies)
app.include_router(warehouse_zone_router, dependencies=protected_dependencies)
app.include_router(shipment_router, dependencies=protected_dependencies)
app.include_router(procurement_request_router, dependencies=protected_dependencies)
app.include_router(dashboard_router, dependencies=protected_dependencies)
app.include_router(audit_router, dependencies=protected_dependencies)
app.include_router(system_jobs_router, dependencies=protected_dependencies)

# AI
app.include_router(procurement_ai_router, dependencies=protected_dependencies)
app.include_router(ai_router, dependencies=protected_dependencies)
app.include_router(ai_chat_router, dependencies=protected_dependencies)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to PharmaChain API 🚀"
    }


# ----------------------------
# Health Check
# ----------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
