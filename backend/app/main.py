from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine

from app.models.base import Base
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.warehouse_zone import WarehouseZone
from app.models.inventory import Inventory
from app.models.shipment import Shipment
from app.models.procurement_request import ProcurementRequest

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


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PharmaChain API",
    version="0.1.0"
)

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
app.include_router(product_router)
app.include_router(supplier_router)
app.include_router(inventory_router)
app.include_router(warehouse_zone_router)
app.include_router(shipment_router)
app.include_router(procurement_request_router)
app.include_router(dashboard_router)

# AI
app.include_router(procurement_ai_router)
app.include_router(ai_router)
app.include_router(ai_chat_router)

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