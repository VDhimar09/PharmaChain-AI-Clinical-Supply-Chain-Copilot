"""Planning context objects for reasoning plan generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlannerContext:
    """
    Immutable planning input passed to a planning strategy.

    Attributes:
        user_message: Raw user request to be planned.
        detected_intent: Intent identified before strategy execution.
        available_tools: Ordered list of tools available for planning.
        metadata: Optional planner metadata for future extensions.
    """

    user_message: str
    detected_intent: str
    available_tools: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
