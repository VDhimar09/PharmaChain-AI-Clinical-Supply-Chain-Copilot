from dataclasses import dataclass, field
from typing import List


@dataclass
class ExecutionPlan:
    """
    Represents the ordered list of tools required
    to satisfy a user request.
    """

    user_request: str

    tools: List[str] = field(default_factory=list)

    reasoning: str = ""

    def add_tool(self, tool_name: str) -> None:
        """Add a tool only once while preserving order."""
        if tool_name not in self.tools:
            self.tools.append(tool_name)

    @property
    def tool_count(self) -> int:
        return len(self.tools)

    def is_empty(self) -> bool:
        return len(self.tools) == 0