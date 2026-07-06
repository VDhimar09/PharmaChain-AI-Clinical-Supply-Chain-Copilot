from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.ai.intent_engine import IntentEngine
from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.reasoning.reasoning_engine import ReasoningEngine
from app.ai.response import ResponseComposer
from app.ai.tools.ai_insights_tool import AIInsightsTool
from app.ai.tools.inventory_tool import InventoryTool
from app.ai.tools.procurement_tool import ProcurementTool
from app.ai.tools.shipment_tool import ShipmentTool
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.tools.warehouse_tool import WarehouseTool
from app.schemas.ai_copilot import CopilotChatResponse


class CopilotOrchestratorService:
    def __init__(self, db: Session):
        self.db = db
        self.registry = ToolRegistry()
        self.registry.register(InventoryTool())
        self.registry.register(WarehouseTool())
        self.registry.register(ShipmentTool())
        self.registry.register(ProcurementTool())
        self.registry.register(AIInsightsTool())
        self.planner = ReasoningPlanner()
        self.reasoning_engine = ReasoningEngine(
            planner=self.planner,
            registry=self.registry,
        )
        self.response_composer = ResponseComposer()

    def chat(self, message: str) -> CopilotChatResponse:
        intent = IntentEngine.detect(message)
        result = self.reasoning_engine.execute(
            message=message,
            db=self.db,
        )
        composed = self.response_composer.compose_copilot_response(
            intent=intent,
            result=result,
        )

        return CopilotChatResponse(
            conversation_id=uuid4(),
            generated_at=datetime.now(UTC),
            intent=intent,
            confidence=composed["confidence"],
            tools_used=composed["tools_used"],
            reasoning=composed["reasoning"],
            tool_execution=composed["tool_execution"],
            evidence=composed["evidence"],
            recommendations=composed["recommendations"],
            response=composed["response"],
        )
