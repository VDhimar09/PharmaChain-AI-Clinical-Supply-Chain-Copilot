from time import perf_counter
from typing import Any, Dict

from app.ai.exceptions import ToolExecutionException
from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.tools.tool_registry import ToolRegistry
from app.core.logging import get_logger


logger = get_logger(__name__)


class ReasoningEngine:
    """
    Executes an execution plan by invoking tools
    from the Tool Registry in order.

    The engine is intentionally unaware of the
    concrete implementations of individual tools.
    """

    def __init__(
        self,
        planner: ReasoningPlanner,
        registry: ToolRegistry,
    ):
        self.planner = planner
        self.registry = registry

    def execute(
        self,
        message: str,
        **context: Any,
    ) -> Dict[str, Any]:
        """
        Build a plan and execute each tool.

        Returns structured evidence for the AI layer.
        """
        logger.info("Incoming reasoning request: %s", message)
        started_at = perf_counter()

        plan = self.planner.build_plan(message)
        logger.info("Executing plan with tools=%s", plan.tools)

        evidence = {}

        for tool_name in plan.tools:
            tool_started_at = perf_counter()

            try:
                logger.info("Executing tool: %s", tool_name)
                tool = self.registry.get(tool_name)

                result = tool.run(
                    message=message,
                    **context,
                )

                evidence[tool_name] = result
                logger.info(
                    "Tool execution completed: %s duration_ms=%.2f",
                    tool_name,
                    (perf_counter() - tool_started_at) * 1000,
                )
            except Exception as exc:
                logger.exception("Tool execution failed: %s", tool_name)
                raise ToolExecutionException(
                    f"Tool execution failed for '{tool_name}'."
                ) from exc

        logger.info(
            "Reasoning execution completed duration_ms=%.2f",
            (perf_counter() - started_at) * 1000,
        )

        return {
            "user_request": message,
            "reasoning": plan.reasoning,
            "plan": plan.tools,
            "tool_results": evidence,
        }
