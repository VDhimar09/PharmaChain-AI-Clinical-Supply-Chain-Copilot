import pytest

from app.ai.tools.base_tool import BaseTool
from app.ai.tools.tool_registry import ToolRegistry


class StubTool(BaseTool):
    def __init__(self, tool_name: str) -> None:
        self._tool_name = tool_name

    @property
    def name(self) -> str:
        return self._tool_name

    @property
    def description(self) -> str:
        return f"{self._tool_name} tool"

    def run(self, *args, **kwargs) -> dict:
        return {"tool": self._tool_name}


def test_tool_registry_registers_and_returns_tools() -> None:
    registry = ToolRegistry()
    tool = StubTool("inventory")

    registry.register(tool)

    assert registry.exists("inventory") is True
    assert registry.get("inventory") is tool
    assert registry.list_tools() == ["inventory"]


def test_tool_registry_rejects_duplicate_registration() -> None:
    registry = ToolRegistry()
    registry.register(StubTool("inventory"))

    with pytest.raises(ValueError) as exc_info:
        registry.register(StubTool("inventory"))

    assert "Tool 'inventory' is already registered." in str(exc_info.value)


def test_tool_registry_raises_for_unknown_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError) as exc_info:
        registry.get("shipment")

    assert "Unknown tool 'shipment'." in str(exc_info.value)
