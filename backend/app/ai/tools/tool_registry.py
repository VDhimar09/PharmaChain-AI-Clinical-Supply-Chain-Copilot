from typing import Dict, List

from app.ai.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Central registry for all AI tools.

    The Reasoning Engine uses this registry to
    discover and retrieve tools dynamically.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Raises:
            ValueError: if a duplicate tool name is registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Retrieve a tool by name.

        Raises:
            KeyError: if the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(
                f"Unknown tool '{name}'."
            )

        return self._tools[name]

    def list_tools(self) -> List[str]:
        """Return all registered tool names."""
        return list(self._tools.keys())

    def exists(self, name: str) -> bool:
        """Check whether a tool is registered."""
        return name in self._tools