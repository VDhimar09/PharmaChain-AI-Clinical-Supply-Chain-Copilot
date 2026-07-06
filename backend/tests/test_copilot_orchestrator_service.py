from app.schemas.ai_copilot import CopilotChatResponse
from app.services.copilot_orchestrator_service import CopilotOrchestratorService


def test_copilot_orchestrator_service_returns_structured_response(monkeypatch):
    monkeypatch.setattr(
        "app.services.copilot_orchestrator_service.IntentEngine.detect",
        lambda message: "EXECUTIVE_SUMMARY",
    )
    monkeypatch.setattr(
        "app.services.copilot_orchestrator_service.ReasoningEngine.execute",
        lambda self, message, db: {
            "user_request": message,
            "reasoning": "Executive summary requires inventory, warehouse, shipment, and AI insights evidence.",
            "plan": ["inventory", "warehouse", "shipment", "ai_insights"],
            "tool_results": {
                "inventory": {
                    "low_stock_products": 3,
                    "total_available_quantity": 1400,
                    "total_inventory_items": 28,
                },
                "warehouse": {
                    "occupancy_percentage": 81,
                    "available_capacity": 220,
                },
                "shipment": {
                    "delayed_shipments": 2,
                    "inbound_shipments": 5,
                    "outbound_shipments": 4,
                },
                "ai_insights": {
                    "confidence": 96,
                    "alerts": [
                        {
                            "severity": "HIGH",
                            "title": "Cold chain",
                            "message": "Zone B is near capacity.",
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Increase Safety Stock",
                            "message": "Increase Vaccine A safety stock by 20%.",
                        }
                    ],
                    "procurement": {
                        "pending": [],
                        "approved": [],
                        "rejected": [],
                    },
                },
            },
            "tool_execution": [
                {
                    "tool": "Inventory Tool",
                    "tool_key": "inventory",
                    "status": "SUCCESS",
                    "execution_time_ms": 12.4,
                },
                {
                    "tool": "Warehouse Tool",
                    "tool_key": "warehouse",
                    "status": "SUCCESS",
                    "execution_time_ms": 10.8,
                },
                {
                    "tool": "Shipment Tool",
                    "tool_key": "shipment",
                    "status": "SUCCESS",
                    "execution_time_ms": 14.2,
                },
                {
                    "tool": "AI Insights Tool",
                    "tool_key": "ai_insights",
                    "status": "SUCCESS",
                    "execution_time_ms": 30.1,
                },
            ],
        },
    )

    service = CopilotOrchestratorService(db=object())
    result = service.chat("What should I prioritise today?")

    assert isinstance(result, CopilotChatResponse)
    assert result.intent == "EXECUTIVE_SUMMARY"
    assert result.confidence == 96
    assert result.tools_used == [
        "Inventory Tool",
        "Warehouse Tool",
        "Shipment Tool",
        "AI Insights Tool",
    ]
    assert result.reasoning[0].step == "Inventory Analysis"
    assert result.evidence.inventory["low_stock_products"] == 3
    assert result.recommendations[0].startswith("Increase Safety Stock")
    assert "highest operational priorities" in result.response
