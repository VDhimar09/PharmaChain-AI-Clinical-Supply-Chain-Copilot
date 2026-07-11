from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User
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
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Copilot"]
)

inventory_tool = InventoryTool()
warehouse_tool = WarehouseTool()
shipment_tool = ShipmentTool()


@router.get("/inventory-summary")
def inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return inventory_tool.get_inventory_summary(db)


@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return inventory_tool.get_low_stock_products(db)


@router.get("/expiring")
def expiring_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return inventory_tool.get_expiring_products(db)


@router.get("/warehouse-capacity")
def warehouse_capacity(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return warehouse_tool.get_capacity_summary(db)


@router.get("/shipment-summary")
def shipment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    return shipment_tool.get_shipment_summary(db)


@router.get(
    "/insights",
    response_model=AIInsightsResponse,
)
def get_ai_insights(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("insights.view")
    ),
):
    service = AIInsightsService(db)
    insights = service.get_insights()
    insights_data = jsonable_encoder(
        insights
    )

    AuditService.enqueue_log(
        background_tasks,
        action="AI_INSIGHTS_VIEWED",
        resource_type="AI",
        status_code=200,
        request=request,
        user=current_user,
        details={
            "response_generated": True,
            "confidence": insights_data.get("confidence"),
        },
    )

    return insights


@router.post(
    "/copilot/chat",
    response_model=CopilotChatResponse,
)
def copilot_chat(
    request_context: Request,
    background_tasks: BackgroundTasks,
    request: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("copilot.use")
    ),
):
    service = CopilotOrchestratorService(db)
    response = service.chat(request.message)
    response_data = jsonable_encoder(
        response
    )

    AuditService.enqueue_log(
        background_tasks,
        action="COPILOT_CHAT",
        resource_type="AI",
        status_code=200,
        request=request_context,
        user=current_user,
        details={
            "prompt": request.message,
            "response_generated": True,
            "tools_used": response_data.get("tools_used"),
            "tool_execution": response_data.get("tool_execution"),
            "intent": response_data.get("intent"),
        },
    )

    return response


@router.post(
    "/procurement/analyze",
    response_model=ProcurementAnalysisResponse,
)
def analyze_procurement(
    request_context: Request,
    background_tasks: BackgroundTasks,
    request: ProcurementAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("ai.access")
    ),
):
    service = ProcurementAnalysisService(db)

    try:
        response = service.analyze(
            product_id=request.product_id,
            supplier_id=request.supplier_id,
            requested_quantity=request.requested_quantity,
        )
        response_data = jsonable_encoder(
            response
        )

        AuditService.enqueue_log(
            background_tasks,
            action="AI_PROCUREMENT_ANALYSIS",
            resource_type="AI",
            status_code=200,
            request=request_context,
            user=current_user,
            details={
                "product_id": request.product_id,
                "supplier_id": request.supplier_id,
                "requested_quantity": request.requested_quantity,
                "decision": response_data.get("decision"),
                "response_generated": True,
                "tool_execution": response_data.get("tool_execution"),
            },
        )

        return response
    except ProcurementEvaluationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
