class IntentEngine:
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    INVENTORY_STATUS = "INVENTORY_STATUS"
    WAREHOUSE_STATUS = "WAREHOUSE_STATUS"
    SHIPMENT_STATUS = "SHIPMENT_STATUS"
    PROCUREMENT = "PROCUREMENT"
    PROCUREMENT_STATUS = "PROCUREMENT_STATUS"
    AI_INSIGHTS = "AI_INSIGHTS"
    RISK_SUMMARY = "RISK_SUMMARY"
    UNKNOWN = "UNKNOWN"

    # Backwards-compatible aliases.
    INVENTORY = INVENTORY_STATUS
    WAREHOUSE = WAREHOUSE_STATUS
    SHIPMENT = SHIPMENT_STATUS

    @staticmethod
    def detect(message: str):
        text = message.lower().strip()

        executive_keywords = [
            "what should i prioritise today",
            "what should i prioritize today",
            "summarise today's operations",
            "summarize today's operations",
            "summarise todays operations",
            "summarize todays operations",
            "today's operations",
            "todays operations",
        ]

        ai_insight_keywords = [
            "ai recommendations",
            "ai recommendation",
            "ai insight",
            "ai insights",
            "show ai recommendations",
            "explain today's ai recommendations",
            "explain todays ai recommendations",
        ]

        risk_keywords = [
            "risk",
            "risks",
            "priority",
            "priorities",
            "attention",
            "urgent",
            "critical alert",
            "critical alerts",
        ]

        procurement_keywords = [
            "reorder",
            "order",
            "purchase",
            "procure",
            "buy",
            "supplier",
            "receive shipment",
            "receive another shipment",
            "should i order",
            "should i reorder",
            "can we receive",
            "can i order",
            "why was this procurement rejected",
        ]

        procurement_status_keywords = [
            "procurement request",
            "procurement requests",
            "requests require review",
            "which procurement requests",
            "pending procurements",
            "pending procurement",
            "approved procurement",
            "rejected procurement",
        ]

        shipment_keywords = [
            "shipment",
            "shipments",
            "delivery",
            "deliveries",
            "transport",
            "inbound",
            "outbound",
            "delayed",
            "arrival",
        ]

        warehouse_keywords = [
            "warehouse",
            "capacity",
            "occupancy",
            "space",
            "zone",
            "storage",
        ]

        inventory_keywords = [
            "inventory",
            "stock",
            "quantity",
            "available",
            "expiry",
            "expire",
            "medicine",
            "vaccine",
            "low in stock",
            "close to expiry",
        ]

        for phrase in executive_keywords:
            if phrase in text:
                return IntentEngine.EXECUTIVE_SUMMARY

        for phrase in ai_insight_keywords:
            if phrase in text:
                return IntentEngine.AI_INSIGHTS

        if any(word in text for word in risk_keywords):
            return IntentEngine.RISK_SUMMARY

        for word in procurement_keywords:
            if word in text:
                return IntentEngine.PROCUREMENT

        for word in procurement_status_keywords:
            if word in text:
                return IntentEngine.PROCUREMENT_STATUS

        for word in shipment_keywords:
            if word in text:
                return IntentEngine.SHIPMENT_STATUS

        for word in warehouse_keywords:
            if word in text:
                return IntentEngine.WAREHOUSE_STATUS

        for word in inventory_keywords:
            if word in text:
                return IntentEngine.INVENTORY_STATUS

        return IntentEngine.UNKNOWN
