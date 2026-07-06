from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ai.tools.inventory_tool import InventoryTool
from app.schemas.procurement_ai import (
    ProcurementAnalysisRequest,
    ProcurementAnalysisResponse,
)
from app.schemas.ai_insights import AIInsightsResponse
from app.schemas.ai_copilot import CopilotChatRequest, CopilotChatResponse
from app.ai.tools.warehouse_tool import WarehouseTool
from app.ai.tools.shipment_tool import ShipmentTool
from app.services.procurement_ai_service import ProcurementEvaluationError
from app.services.ai_insights_service import AIInsightsService
from app.services.copilot_orchestrator_service import CopilotOrchestratorService
from app.services.procurement_analysis_service import ProcurementAnalysisService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Copilot"]
)

inventory_tool = InventoryTool()
warehouse_tool = WarehouseTool()
shipment_tool = ShipmentTool()


@router.get("/inventory-summary")
def inventory_summary(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_inventory_summary(db)


@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_low_stock_products(db)


@router.get("/expiring")
def expiring_products(
    db: Session = Depends(get_db)
):
    return inventory_tool.get_expiring_products(db)


@router.get("/warehouse-capacity")
def warehouse_capacity(
    db: Session = Depends(get_db)
):
    return warehouse_tool.get_capacity_summary(db)


@router.get("/shipment-summary")
def shipment_summary(
    db: Session = Depends(get_db)
):
    return shipment_tool.get_shipment_summary(db)


@router.get(
    "/insights",
    response_model=AIInsightsResponse,
)
def get_ai_insights(
    db: Session = Depends(get_db),
):
    service = AIInsightsService(db)
    return service.get_insights()


@router.post(
    "/copilot/chat",
    response_model=CopilotChatResponse,
)
def copilot_chat(
    request: CopilotChatRequest,
    db: Session = Depends(get_db),
):
    service = CopilotOrchestratorService(db)
    return service.chat(request.message)


@router.post(
    "/procurement/analyze",
    response_model=ProcurementAnalysisResponse,
)
def analyze_procurement(
    request: ProcurementAnalysisRequest,
    db: Session = Depends(get_db),
):
    service = ProcurementAnalysisService(db)

    try:
        return service.analyze(
            product_id=request.product_id,
            supplier_id=request.supplier_id,
            requested_quantity=request.requested_quantity,
        )
    except ProcurementEvaluationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
