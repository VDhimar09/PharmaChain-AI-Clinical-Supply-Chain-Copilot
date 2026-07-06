from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.schemas.ai_insights import (
    AIInsightsResponse,
    ExecutiveSummary,
    InsightAlert,
    InsightRecommendation,
    InventoryInsightItem,
    InventoryInsights,
    ProcurementInsightItem,
    ProcurementInsights,
    ShipmentInsightItem,
    ShipmentInsights,
    TrendData,
    TrendPoint,
    WarehouseInsightItem,
    WarehouseInsights,
)
from app.services.dashboard_service import DashboardService
from app.services.inventory_service import InventoryService
from app.services.procurement_request_service import ProcurementRequestService
from app.services.shipment_service import ShipmentService
from app.services.warehouse_zone_service import WarehouseZoneService


class AIInsightsService:
    """
    Aggregates live operational data for the AI Insights page.

    The service reuses the existing domain services and keeps all
    recommendation logic on the backend so the frontend remains a
    typed presentation layer.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_insights(self) -> AIInsightsResponse:
        generated_at = datetime.now(UTC)

        inventory_items = InventoryService.get_inventory(self.db)
        low_stock_items = InventoryService.get_low_stock_products(self.db)
        near_expiry_items = InventoryService.get_expiring_products(self.db, days=60)
        warehouse_zones = WarehouseZoneService.get_zones(self.db)
        shipments = ShipmentService.get_shipments(self.db)
        procurement_requests = ProcurementRequestService.get_procurement_requests(self.db)
        dashboard_summary = DashboardService.get_summary(self.db)

        inventory_insights = self._build_inventory_insights(
            inventory_items=inventory_items,
            low_stock_items=low_stock_items,
            near_expiry_items=near_expiry_items,
        )
        warehouse_insights = self._build_warehouse_insights(warehouse_zones)
        shipment_insights = self._build_shipment_insights(shipments)
        procurement_insights = self._build_procurement_insights(procurement_requests)
        alerts = self._build_alerts(
            inventory_insights=inventory_insights,
            warehouse_insights=warehouse_insights,
            shipment_insights=shipment_insights,
            procurement_insights=procurement_insights,
        )
        recommendations = self._build_recommendations(
            inventory_insights=inventory_insights,
            warehouse_insights=warehouse_insights,
            shipment_insights=shipment_insights,
            procurement_insights=procurement_insights,
        )

        return AIInsightsResponse(
            generated_at=generated_at,
            confidence=self._calculate_confidence(
                inventory_items=inventory_items,
                warehouse_zones=warehouse_zones,
                shipments=shipments,
                procurement_requests=procurement_requests,
            ),
            executive_summary=ExecutiveSummary(
                # Pricing is not stored in the current schema, so we reuse the
                # total tracked inventory units until valuation data exists.
                inventory_value=dashboard_summary["total_inventory_units"],
                warehouse_utilisation=round(dashboard_summary["warehouse_occupancy"]),
                pending_procurements=len(procurement_insights.pending),
                critical_alerts=len(
                    [alert for alert in alerts if alert.severity == "HIGH"]
                ),
            ),
            inventory=inventory_insights,
            warehouse=warehouse_insights,
            shipments=shipment_insights,
            procurement=procurement_insights,
            alerts=alerts,
            recommendations=recommendations,
            trend_data=TrendData(
                inventory=self._build_inventory_trends(inventory_items),
                shipments=self._build_shipment_trends(shipments),
                warehouse=self._build_warehouse_trends(warehouse_zones),
            ),
        )

    def _build_inventory_insights(
        self,
        inventory_items: list,
        low_stock_items: list,
        near_expiry_items: list,
    ) -> InventoryInsights:
        overstock_items = [
            item
            for item in inventory_items
            if getattr(item.product, "safety_stock", 0) > 0
            and item.available_quantity >= item.product.safety_stock * 3
        ]
        fast_moving_items = [
            item
            for item in inventory_items
            if item.quantity > 0
            and item.reserved_quantity / item.quantity >= 0.4
        ]
        slow_moving_items = [
            item
            for item in inventory_items
            if item.available_quantity > getattr(item.product, "safety_stock", 0) * 2
            and item.reserved_quantity == 0
        ]

        return InventoryInsights(
            low_stock=self._serialize_inventory_items(low_stock_items, limit=5),
            overstock=self._serialize_inventory_items(overstock_items, limit=5),
            near_expiry=self._serialize_inventory_items(near_expiry_items, limit=5),
            fast_moving=self._serialize_inventory_items(fast_moving_items, limit=5),
            slow_moving=self._serialize_inventory_items(slow_moving_items, limit=5),
        )

    def _build_warehouse_insights(self, warehouse_zones: list) -> WarehouseInsights:
        ordered_by_occupancy = sorted(
            warehouse_zones,
            key=self._zone_occupancy_percentage,
            reverse=True,
        )
        cold_chain_zones = [
            zone
            for zone in warehouse_zones
            if (
                "cold" in zone.zone_type.lower()
                or (zone.temperature_max is not None and zone.temperature_max <= 8)
            )
        ]
        available_capacity = sorted(
            warehouse_zones,
            key=lambda zone: max(zone.capacity_units - zone.occupied_units, 0),
            reverse=True,
        )

        return WarehouseInsights(
            occupancy=self._serialize_warehouse_zones(ordered_by_occupancy[:5]),
            cold_chain=self._serialize_warehouse_zones(
                sorted(cold_chain_zones, key=self._zone_occupancy_percentage, reverse=True)[:5]
            ),
            available_capacity=self._serialize_warehouse_zones(available_capacity[:5]),
        )

    def _build_shipment_insights(self, shipments: list) -> ShipmentInsights:
        incoming = [
            shipment for shipment in shipments if shipment.shipment_type == "INBOUND"
        ]
        outgoing = [
            shipment for shipment in shipments if shipment.shipment_type == "OUTBOUND"
        ]
        delayed = [
            shipment for shipment in shipments if shipment.status.lower() == "delayed"
        ]

        return ShipmentInsights(
            incoming=self._serialize_shipments(
                sorted(incoming, key=lambda shipment: shipment.expected_arrival)[:5]
            ),
            outgoing=self._serialize_shipments(
                sorted(outgoing, key=lambda shipment: shipment.expected_arrival)[:5]
            ),
            delayed=self._serialize_shipments(
                sorted(delayed, key=lambda shipment: shipment.expected_arrival)[:5]
            ),
        )

    def _build_procurement_insights(self, procurement_requests: list) -> ProcurementInsights:
        pending = [
            request for request in procurement_requests if request.status == "PENDING"
        ]
        approved = [
            request for request in procurement_requests if request.status == "APPROVED"
        ]
        rejected = [
            request for request in procurement_requests if request.status == "REJECTED"
        ]

        return ProcurementInsights(
            pending=self._serialize_procurement_requests(
                sorted(pending, key=lambda request: request.created_at, reverse=True)[:5]
            ),
            approved=self._serialize_procurement_requests(
                sorted(approved, key=lambda request: request.created_at, reverse=True)[:5]
            ),
            rejected=self._serialize_procurement_requests(
                sorted(rejected, key=lambda request: request.created_at, reverse=True)[:5]
            ),
        )

    def _build_alerts(
        self,
        inventory_insights: InventoryInsights,
        warehouse_insights: WarehouseInsights,
        shipment_insights: ShipmentInsights,
        procurement_insights: ProcurementInsights,
    ) -> list[InsightAlert]:
        alerts: list[InsightAlert] = []

        if inventory_insights.low_stock:
            item = inventory_insights.low_stock[0]
            alerts.append(
                InsightAlert(
                    severity="HIGH",
                    title="Low Stock Risk",
                    message=(
                        f"{item.product_name} has only {item.available_quantity} units "
                        f"available in {item.warehouse_zone}."
                    ),
                )
            )

        if inventory_insights.near_expiry:
            item = inventory_insights.near_expiry[0]
            alerts.append(
                InsightAlert(
                    severity="HIGH" if (item.days_to_expiry or 0) <= 14 else "MEDIUM",
                    title="Near Expiry Exposure",
                    message=(
                        f"{item.product_name} expires in {item.days_to_expiry or 0} days. "
                        "Prioritize allocation or redistribution."
                    ),
                )
            )

        high_occupancy_zone = next(
            (
                zone
                for zone in warehouse_insights.occupancy
                if zone.occupancy_percentage >= 90
            ),
            None,
        )
        if high_occupancy_zone is not None:
            alerts.append(
                InsightAlert(
                    severity="HIGH",
                    title="Warehouse Capacity Pressure",
                    message=(
                        f"{high_occupancy_zone.name} is at "
                        f"{high_occupancy_zone.occupancy_percentage}% occupancy."
                    ),
                )
            )

        delayed_shipment = shipment_insights.delayed[0] if shipment_insights.delayed else None
        if delayed_shipment is not None:
            alerts.append(
                InsightAlert(
                    severity="HIGH",
                    title="Delayed Shipment",
                    message=(
                        f"{delayed_shipment.shipment_number} for "
                        f"{delayed_shipment.product_name} is delayed."
                    ),
                )
            )

        if len(procurement_insights.pending) >= 5:
            alerts.append(
                InsightAlert(
                    severity="MEDIUM",
                    title="Procurement Backlog",
                    message=(
                        f"{len(procurement_insights.pending)} procurement requests are "
                        "still awaiting review."
                    ),
                )
            )

        return alerts[:6]

    def _build_recommendations(
        self,
        inventory_insights: InventoryInsights,
        warehouse_insights: WarehouseInsights,
        shipment_insights: ShipmentInsights,
        procurement_insights: ProcurementInsights,
    ) -> list[InsightRecommendation]:
        recommendations: list[InsightRecommendation] = []

        if inventory_insights.low_stock:
            item = inventory_insights.low_stock[0]
            recommendations.append(
                InsightRecommendation(
                    priority="HIGH",
                    title="Increase Safety Stock",
                    message=(
                        f"Raise replenishment coverage for {item.product_name} and "
                        "trigger supplier follow-up before stock falls further."
                    ),
                )
            )

        if inventory_insights.near_expiry:
            item = inventory_insights.near_expiry[0]
            recommendations.append(
                InsightRecommendation(
                    priority="HIGH" if (item.days_to_expiry or 0) <= 14 else "MEDIUM",
                    title="Redistribute Near-Expiry Inventory",
                    message=(
                        f"Move or consume {item.product_name} before {item.expiry_date} "
                        "to reduce expiry losses."
                    ),
                )
            )

        cold_chain_zone = next(
            (
                zone
                for zone in warehouse_insights.cold_chain
                if zone.occupancy_percentage >= 85
            ),
            None,
        )
        if cold_chain_zone is not None:
            recommendations.append(
                InsightRecommendation(
                    priority="HIGH",
                    title="Protect Cold-Chain Capacity",
                    message=(
                        f"Rebalance inventory away from {cold_chain_zone.name} to keep "
                        "temperature-controlled capacity available."
                    ),
                )
            )

        if shipment_insights.delayed:
            delayed_by_supplier = Counter(
                shipment.supplier_name for shipment in shipment_insights.delayed
            )
            supplier_name, delayed_count = delayed_by_supplier.most_common(1)[0]
            recommendations.append(
                InsightRecommendation(
                    priority="MEDIUM" if delayed_count == 1 else "HIGH",
                    title="Address Supplier Delivery Risk",
                    message=(
                        f"Review carrier and supplier performance for {supplier_name}; "
                        f"{delayed_count} active shipment(s) are behind schedule."
                    ),
                )
            )

        if len(procurement_insights.pending) >= 3:
            recommendations.append(
                InsightRecommendation(
                    priority="MEDIUM",
                    title="Clear Procurement Bottlenecks",
                    message=(
                        "Prioritize aging pending requests to reduce downstream stock and "
                        "capacity risk."
                    ),
                )
            )

        if inventory_insights.overstock:
            item = inventory_insights.overstock[0]
            recommendations.append(
                InsightRecommendation(
                    priority="LOW",
                    title="Reduce Overstock Exposure",
                    message=(
                        f"Review reorder thresholds for {item.product_name} to avoid "
                        "tying up warehouse capacity."
                    ),
                )
            )

        return recommendations[:6]

    def _build_inventory_trends(self, inventory_items: list) -> list[TrendPoint]:
        monthly_totals: dict[str, dict[str, int]] = defaultdict(
            lambda: {"received_units": 0, "available_units": 0}
        )

        for item in inventory_items:
            label = item.received_at.strftime("%b %Y")
            monthly_totals[label]["received_units"] += item.quantity
            monthly_totals[label]["available_units"] += item.available_quantity

        return [
            TrendPoint(
                label=label,
                value=values["received_units"],
                secondary_value=values["available_units"],
            )
            for label, values in sorted(
                monthly_totals.items(),
                key=lambda entry: datetime.strptime(entry[0], "%b %Y"),
            )[-6:]
        ]

    def _build_shipment_trends(self, shipments: list) -> list[TrendPoint]:
        monthly_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "delayed": 0}
        )

        for shipment in shipments:
            label = shipment.expected_arrival.strftime("%b %Y")
            monthly_counts[label]["total"] += 1
            if shipment.status.lower() == "delayed":
                monthly_counts[label]["delayed"] += 1

        return [
            TrendPoint(
                label=label,
                value=values["total"],
                secondary_value=values["delayed"],
            )
            for label, values in sorted(
                monthly_counts.items(),
                key=lambda entry: datetime.strptime(entry[0], "%b %Y"),
            )[-6:]
        ]

    def _build_warehouse_trends(self, warehouse_zones: list) -> list[TrendPoint]:
        ordered_zones = sorted(
            warehouse_zones,
            key=self._zone_occupancy_percentage,
            reverse=True,
        )
        return [
            TrendPoint(
                label=zone.name,
                value=zone.occupied_units,
                secondary_value=max(zone.capacity_units - zone.occupied_units, 0),
            )
            for zone in ordered_zones[:6]
        ]

    def _calculate_confidence(
        self,
        inventory_items: list,
        warehouse_zones: list,
        shipments: list,
        procurement_requests: list,
    ) -> int:
        domain_count = sum(
            1
            for values in (
                inventory_items,
                warehouse_zones,
                shipments,
                procurement_requests,
            )
            if values
        )
        return min(99, 65 + domain_count * 8)

    def _serialize_inventory_items(
        self,
        inventory_items: Iterable,
        limit: int,
    ) -> list[InventoryInsightItem]:
        serialized_items: list[InventoryInsightItem] = []
        for item in list(inventory_items)[:limit]:
            days_to_expiry = None
            if item.expiry_date is not None:
                days_to_expiry = (item.expiry_date - date.today()).days

            serialized_items.append(
                InventoryInsightItem(
                    id=item.id,
                    product_name=item.product_name,
                    sku=item.sku,
                    category=item.category,
                    warehouse_zone=item.warehouse_zone,
                    quantity=item.quantity,
                    available_quantity=item.available_quantity,
                    reserved_quantity=item.reserved_quantity,
                    expiry_date=item.expiry_date,
                    days_to_expiry=days_to_expiry,
                    status=item.status,
                )
            )
        return serialized_items

    def _serialize_warehouse_zones(self, warehouse_zones: Iterable) -> list[WarehouseInsightItem]:
        return [
            WarehouseInsightItem(
                id=zone.id,
                name=zone.name,
                zone_type=zone.zone_type,
                capacity_units=zone.capacity_units,
                occupied_units=zone.occupied_units,
                available_capacity=max(zone.capacity_units - zone.occupied_units, 0),
                occupancy_percentage=self._zone_occupancy_percentage(zone),
                temperature_min=zone.temperature_min,
                temperature_max=zone.temperature_max,
                status=self._warehouse_status(zone),
            )
            for zone in warehouse_zones
        ]

    def _serialize_shipments(self, shipments: Iterable) -> list[ShipmentInsightItem]:
        serialized_shipments: list[ShipmentInsightItem] = []
        for shipment in shipments:
            delay_days = None
            if shipment.status.lower() == "delayed":
                delay_days = max(
                    (datetime.now(UTC) - shipment.expected_arrival.replace(tzinfo=UTC)).days,
                    0,
                )

            serialized_shipments.append(
                ShipmentInsightItem(
                    id=shipment.id,
                    shipment_number=shipment.shipment_number,
                    shipment_type=shipment.shipment_type,
                    product_name=shipment.product_name,
                    supplier_name=shipment.supplier_name,
                    quantity=shipment.quantity,
                    status=shipment.status,
                    expected_arrival=shipment.expected_arrival,
                    delay_days=delay_days,
                )
            )
        return serialized_shipments

    def _serialize_procurement_requests(
        self,
        procurement_requests: Iterable,
    ) -> list[ProcurementInsightItem]:
        return [
            ProcurementInsightItem(
                id=request.id,
                product_name=request.product.name if request.product is not None else "",
                requested_quantity=request.requested_quantity,
                priority=request.priority,
                status=request.status,
                ai_recommendation=request.ai_recommendation,
                ai_confidence=request.ai_confidence,
                created_by=request.created_by,
                created_at=request.created_at,
                approved_at=request.approved_at,
            )
            for request in procurement_requests
        ]

    @staticmethod
    def _zone_occupancy_percentage(zone) -> int:
        if zone.capacity_units <= 0:
            return 0
        return round((zone.occupied_units / zone.capacity_units) * 100)

    def _warehouse_status(self, zone) -> str:
        occupancy = self._zone_occupancy_percentage(zone)
        if occupancy >= 90:
            return "Critical"
        if occupancy >= 75:
            return "Warning"
        return "Healthy"
