from sqlalchemy.orm import Session

from app.ai.tools.base_tool import BaseTool
from app.services.ai_insights_service import AIInsightsService


class AIInsightsTool(BaseTool):
    @property
    def name(self) -> str:
        return "ai_insights"

    @property
    def display_name(self) -> str:
        return "AI Insights Tool"

    @property
    def description(self) -> str:
        return "Provides aggregated operational AI insights and recommendations."

    def run(self, **kwargs) -> dict:
        db: Session = kwargs["db"]
        service = AIInsightsService(db)
        return service.get_insights().model_dump(mode="json")
