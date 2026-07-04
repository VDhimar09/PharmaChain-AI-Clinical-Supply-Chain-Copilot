
from sqlalchemy.orm import Session

from app.ai.intent_engine import IntentEngine

from app.ai.response import ResponseComposer
from app.ai.tools.inventory_tool import InventoryTool
from app.ai.tools.warehouse_tool import WarehouseTool
from app.ai.tools.shipment_tool import ShipmentTool
from app.ai.tools.procurement_tool import ProcurementTool

from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.reasoning.reasoning_engine import ReasoningEngine
from app.ai.tools.tool_registry import ToolRegistry


class CopilotTool:

    def __init__(self, db: Session):
        self.db = db

        # ==========================================
        # AI Tools
        # ==========================================

        self.inventory_tool = InventoryTool()
        self.warehouse_tool = WarehouseTool()
        self.shipment_tool = ShipmentTool()
        self.procurement_tool = ProcurementTool()

        # ==========================================
        # Tool Registry
        # ==========================================

        self.registry = ToolRegistry()

        self.registry.register(self.inventory_tool)
        self.registry.register(self.warehouse_tool)
        self.registry.register(self.shipment_tool)
        self.registry.register(self.procurement_tool)

        # ==========================================
        # Reasoning Planner
        # ==========================================

        self.planner = ReasoningPlanner()

        # ==========================================
        # Reasoning Engine
        # ==========================================

        self.reasoning_engine = ReasoningEngine(
            planner=self.planner,
            registry=self.registry,
        )
        self.response_composer = ResponseComposer()

    def chat(self, message: str) -> str:

        intent = IntentEngine.detect(message)

        # ==========================================
        # Inventory
        # ==========================================

        if intent == IntentEngine.INVENTORY:

            inventory = self.inventory_tool.get_inventory_summary(
                self.db
            )

            return (
                f"📦 Inventory Summary\n\n"
                f"• Total Inventory Items: "
                f"{inventory['total_inventory_items']}\n"
                f"• Total Units: "
                f"{inventory['total_quantity']}\n"
                f"• Available Units: "
                f"{inventory['total_available_quantity']}\n"
                f"• Reserved Units: "
                f"{inventory['total_reserved_quantity']}"
            )

        # ==========================================
        # Warehouse
        # ==========================================

        elif intent == IntentEngine.WAREHOUSE:

            warehouse = self.warehouse_tool.get_capacity_summary(
                self.db
            )

            return (
                f"🏭 Warehouse Capacity\n\n"
                f"• Total Capacity: "
                f"{warehouse['total_capacity']}\n"
                f"• Occupied Capacity: "
                f"{warehouse['occupied_capacity']}\n"
                f"• Available Capacity: "
                f"{warehouse['available_capacity']}\n"
                f"• Occupancy: "
                f"{warehouse['occupancy_percentage']}%"
            )

        # ==========================================
        # Shipments
        # ==========================================

        elif intent == IntentEngine.SHIPMENT:

            shipment = self.shipment_tool.get_shipment_summary(
                self.db
            )

            return (
                f"🚚 Shipment Summary\n\n"
                f"• Total Shipments: "
                f"{shipment['total_shipments']}\n"
                f"• Inbound: "
                f"{shipment['inbound_shipments']}\n"
                f"• Outbound: "
                f"{shipment['outbound_shipments']}\n"
                f"• Delayed: "
                f"{shipment['delayed_shipments']}"
            )

        # ==========================================
        # Procurement
        # ==========================================

        elif intent == IntentEngine.PROCUREMENT:

            result = self.reasoning_engine.execute(
                message=message,
                db=self.db,
            )

            return self.response_composer.compose(result)

        # ==========================================
        # Unknown
        # ==========================================

        return (
            "👋 Welcome to PharmaChain AI Copilot.\n\n"
            "I can currently help with:\n\n"
            "📦 Inventory\n"
            "🏭 Warehouse Capacity\n"
            "🚚 Shipments\n"
            "🤖 Procurement\n\n"
            "Try asking:\n\n"
            "• How much inventory do we have?\n"
            "• Show warehouse capacity\n"
            "• Shipment summary\n"
            "• Should I reorder stock?"
        )
