"""Read-only local MCP server for aggregate PharmaChain inventory data."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.inventory_service import InventoryService


INVENTORY_SUMMARY_FIELDS = (
    "total_inventory_items",
    "total_quantity",
    "total_available_quantity",
    "total_reserved_quantity",
    "low_stock_products",
)


class InventorySummaryProvider:
    """Retrieve a safe, aggregate inventory summary with a short-lived session."""

    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
        inventory_service: type[InventoryService] = InventoryService,
    ) -> None:
        self._session_factory = session_factory
        self._inventory_service = inventory_service

    def get_inventory_summary(self) -> dict[str, int]:
        """Return allowlisted aggregates and always close the database session."""
        db: Session | None = None
        summary: dict[str, int] | None = None
        failed = False

        try:
            db = self._session_factory()
            statistics = self._inventory_service.get_inventory_statistics(db)
            summary = self._allowlisted_summary(statistics)
        except Exception:
            failed = True
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    failed = True

        if failed or summary is None:
            raise ToolError("Inventory summary is temporarily unavailable.")

        return summary

    @staticmethod
    def _allowlisted_summary(statistics: Mapping[str, Any]) -> dict[str, int]:
        """Expose only the five aggregate fields approved for this MCP tool."""
        return {
            field: int(statistics[field])
            for field in INVENTORY_SUMMARY_FIELDS
        }


def create_inventory_mcp_server(
    provider: InventorySummaryProvider | None = None,
) -> MCPServer:
    """Create the local stdio MCP server with its single read-only tool."""
    inventory_provider = provider or InventorySummaryProvider()
    server = MCPServer(
        "PharmaChain Inventory",
        description="Read-only aggregate inventory information for PharmaChain.",
    )

    @server.tool(
        name="get_inventory_summary",
        description="Return aggregate inventory totals and low-stock count only.",
    )
    def get_inventory_summary() -> dict[str, int]:
        """Get safe aggregate inventory information without product-level records."""
        return inventory_provider.get_inventory_summary()

    return server


mcp = create_inventory_mcp_server()


if __name__ == "__main__":
    # Stdio is intentionally used for local MCP hosts. Do not print to stdout:
    # it carries MCP protocol messages between the host and this server.
    mcp.run(transport="stdio")
