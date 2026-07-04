"""Planning strategy abstractions for reasoning plan generation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.planner.execution_plan import ExecutionPlan
from app.ai.planner.planner_context import PlannerContext


class PlanningStrategy(ABC):
    """
    Contract for all planning strategies.

    Concrete implementations decide which tools should be used and
    in what order for a given planning context.
    """

    @abstractmethod
    def build_plan(self, context: PlannerContext) -> ExecutionPlan:
        """
        Build an execution plan from the provided planning context.

        Args:
            context: Structured planning inputs.

        Returns:
            An execution plan describing the ordered tool sequence.
        """

