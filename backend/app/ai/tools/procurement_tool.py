import re

from sqlalchemy.orm import Session

from app.ai.tools.base_tool import BaseTool
from app.services.procurement_ai_service import ProcurementAIService


class ProcurementTool(BaseTool):
    """
    AI Tool for Procurement decisions.

    This tool acts as a thin adapter between the
    Reasoning Engine and ProcurementAIService.
    """

    _MONTH_PATTERN = re.compile(
        r"\b("
        r"january|february|march|april|may|june|"
        r"july|august|september|october|november|december"
        r")\b",
        re.IGNORECASE,
    )

    _QUANTITY_PATTERN = re.compile(
        r"\b(?P<quantity>\d+)\s*pallets?\b",
        re.IGNORECASE,
    )

    _PRODUCT_PATTERNS = (
        re.compile(
            r"\bof\s+(?P<product>.+?)(?="
            r"\s+(?:next|this)\s+(?:week|month)\b|"
            r"\s+in\s+[A-Za-z]+\b|"
            r"[?.!,]|$)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:order|reorder|purchase|procure|buy|receive)\s+"
            r"(?:another\s+shipment\s+of\s+|shipment\s+of\s+)?"
            r"(?P<product>.+?)(?="
            r"\s+(?:next|this)\s+(?:week|month)\b|"
            r"\s+in\s+[A-Za-z]+\b|"
            r"[?.!,]|$)",
            re.IGNORECASE,
        ),
    )

    @property
    def name(self) -> str:
        return "procurement"

    @property
    def description(self) -> str:
        return (
            "Evaluates procurement requests using inventory, "
            "warehouse capacity and shipment information."
        )

    def run(self, **kwargs):
        """
        Standard entry point used by the Reasoning Engine.
        """
        db: Session = kwargs["db"]
        request = self._build_request(kwargs)
        result = self.evaluate_procurement(db, **request)
        return self._normalize_result(result)

    def evaluate_procurement(
        self,
        db: Session,
        product_name: str,
        pallet_quantity: int,
        month: str,
    ):
        service = ProcurementAIService(db)
        return service.evaluate_request(
            product_name=product_name,
            pallet_quantity=pallet_quantity,
            month=month,
        )

    def _build_request(self, kwargs: dict) -> dict:
        message = self._as_text(kwargs.get("message"))
        product_name = (
            self._as_text(kwargs.get("product_name"))
            or self._extract_product_name(message)
        )
        pallet_quantity = self._resolve_pallet_quantity(
            kwargs.get("pallet_quantity"),
            message,
        )
        month = (
            self._as_text(kwargs.get("month"))
            or self._extract_month(message)
        )

        if not product_name:
            raise ValueError(
                "Procurement evaluation requires a product name."
            )

        return {
            "product_name": product_name,
            "pallet_quantity": pallet_quantity,
            "month": month,
        }

    def _normalize_result(self, result: dict) -> dict:
        normalized = dict(result)

        if "reason" not in normalized:
            normalized["reason"] = self._format_reason(
                normalized.get("reasoning")
            )

        return normalized

    def _resolve_pallet_quantity(
        self,
        raw_value,
        message: str,
    ) -> int:
        if isinstance(raw_value, int):
            return raw_value

        if isinstance(raw_value, str) and raw_value.strip().isdigit():
            return int(raw_value.strip())

        match = self._QUANTITY_PATTERN.search(message)
        if match:
            return int(match.group("quantity"))

        raise ValueError(
            "Procurement evaluation requires a pallet quantity."
        )

    def _extract_product_name(self, message: str) -> str:
        for pattern in self._PRODUCT_PATTERNS:
            match = pattern.search(message)
            if match:
                return match.group("product").strip()

        return ""

    def _extract_month(self, message: str) -> str:
        if "next week" in message.lower():
            return "next week"

        if "next month" in message.lower():
            return "next month"

        if "this month" in message.lower():
            return "this month"

        match = self._MONTH_PATTERN.search(message)
        if match:
            return match.group(1)

        return "current month"

    def _format_reason(self, reasoning) -> str:
        if isinstance(reasoning, list):
            return " ".join(
                item.strip()
                for item in reasoning
                if isinstance(item, str) and item.strip()
            )

        return ""

    def _as_text(self, value) -> str:
        if value is None:
            return ""

        return str(value).strip()
