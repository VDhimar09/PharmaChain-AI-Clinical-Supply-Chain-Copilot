from __future__ import annotations

import pytest

from mcp import Client
from mcp.server.mcpserver.exceptions import ToolError

from app.mcp.inventory_server import (
    INVENTORY_SUMMARY_FIELDS,
    InventorySummaryProvider,
    create_inventory_mcp_server,
)


class FakeSession:
    def __init__(self) -> None:
        self.closed = False
        self.close_attempted = False

    def close(self) -> None:
        self.close_attempted = True
        self.closed = True


class FailingCloseSession(FakeSession):
    def close(self) -> None:
        self.close_attempted = True
        raise RuntimeError("database close details must not be exposed")


class SuccessfulInventoryService:
    @staticmethod
    def get_inventory_statistics(session: FakeSession) -> dict[str, int]:
        return {
            "total_inventory_items": 8,
            "total_quantity": 100,
            "total_available_quantity": 75,
            "total_reserved_quantity": 25,
            "low_stock_products": 2,
            "product_names": ["Not exposed"],
        }


class FailingInventoryService:
    @staticmethod
    def get_inventory_statistics(session: FakeSession) -> dict[str, int]:
        raise RuntimeError("database connection details must not be exposed")


def _provider(
    session: FakeSession,
    service: type[SuccessfulInventoryService] | type[FailingInventoryService],
) -> InventorySummaryProvider:
    return InventorySummaryProvider(
        session_factory=lambda: session,
        inventory_service=service,  # type: ignore[arg-type]
    )


def test_provider_returns_only_approved_inventory_aggregates() -> None:
    session = FakeSession()

    result = _provider(session, SuccessfulInventoryService).get_inventory_summary()

    assert result == {
        "total_inventory_items": 8,
        "total_quantity": 100,
        "total_available_quantity": 75,
        "total_reserved_quantity": 25,
        "low_stock_products": 2,
    }
    assert tuple(result) == INVENTORY_SUMMARY_FIELDS


def test_provider_closes_session_after_success() -> None:
    session = FakeSession()

    _provider(session, SuccessfulInventoryService).get_inventory_summary()

    assert session.closed is True


def test_provider_closes_session_after_failure() -> None:
    session = FakeSession()

    with pytest.raises(ToolError, match="Inventory summary is temporarily unavailable"):
        _provider(session, FailingInventoryService).get_inventory_summary()

    assert session.closed is True


def test_provider_returns_safe_error_when_close_fails_after_success() -> None:
    session = FailingCloseSession()

    with pytest.raises(ToolError) as exc_info:
        _provider(session, SuccessfulInventoryService).get_inventory_summary()

    assert str(exc_info.value) == "Inventory summary is temporarily unavailable."
    assert "database close details" not in str(exc_info.value)
    assert session.close_attempted is True


def test_provider_returns_safe_error_when_service_and_close_fail() -> None:
    session = FailingCloseSession()

    with pytest.raises(ToolError) as exc_info:
        _provider(session, FailingInventoryService).get_inventory_summary()

    assert str(exc_info.value) == "Inventory summary is temporarily unavailable."
    assert "database connection details" not in str(exc_info.value)
    assert "database close details" not in str(exc_info.value)
    assert session.close_attempted is True


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_mcp_client_discovers_and_invokes_only_inventory_summary_tool() -> None:
    session = FakeSession()
    server = create_inventory_mcp_server(
        _provider(session, SuccessfulInventoryService)
    )

    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools.tools] == ["get_inventory_summary"]

        result = await client.call_tool("get_inventory_summary", {})

    assert result.is_error is False
    assert result.structured_content == {
        "total_inventory_items": 8,
        "total_quantity": 100,
        "total_available_quantity": 75,
        "total_reserved_quantity": 25,
        "low_stock_products": 2,
    }
    assert session.closed is True


@pytest.mark.anyio
async def test_mcp_client_receives_safe_error_when_inventory_retrieval_fails() -> None:
    session = FailingCloseSession()
    server = create_inventory_mcp_server(
        _provider(session, FailingInventoryService)
    )

    async with Client(server, raise_exceptions=True) as client:
        result = await client.call_tool("get_inventory_summary", {})

    assert result.is_error is True
    assert result.content[0].text == (
        "Error executing tool get_inventory_summary: "
        "Inventory summary is temporarily unavailable."
    )
    assert "database connection details" not in result.content[0].text
    assert "database close details" not in result.content[0].text
    assert session.close_attempted is True
