from app.ai.tools.base_tool import BaseTool


class ProcurementTool(BaseTool):
    """
    AI Tool for Procurement decisions.

    This tool will later evaluate procurement requests
    using inventory, warehouse, shipment and business rules.
    """

    @property
    def name(self) -> str:
        return "procurement"

    @property
    def description(self) -> str:
        return (
            "Evaluates procurement requests using inventory, "
            "warehouse capacity and shipment information."
        )

    def run(self, **kwargs):
        """
        Temporary implementation.

        This will be enhanced in the next sprint to perform
        full procurement reasoning.
        """

        return {
            "decision": "REVIEW",
            "confidence": 0.90,
            "reason": (
                "Procurement reasoning engine will be integrated "
                "in the next implementation step."
            )
        }