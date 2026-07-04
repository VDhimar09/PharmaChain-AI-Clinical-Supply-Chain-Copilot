from sqlalchemy.orm import Session

from app.ai.copilot_tool import CopilotTool


class AIChatService:

    @staticmethod
    def chat(
        db: Session,
        message: str
    ):
        copilot = CopilotTool(db)

        return {
            "response": copilot.chat(message)
        }