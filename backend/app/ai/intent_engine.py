class IntentEngine:

    INVENTORY = "inventory"
    WAREHOUSE = "warehouse"
    SHIPMENT = "shipment"
    PROCUREMENT = "procurement"
    UNKNOWN = "unknown"

    @staticmethod
    def detect(message: str):

        text = message.lower().strip()

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
            "can i order"
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
            "arrival"
        ]

        warehouse_keywords = [
            "warehouse",
            "capacity",
            "occupancy",
            "space",
            "zone",
            "storage"
        ]

        inventory_keywords = [
            "inventory",
            "stock",
            "quantity",
            "available",
            "expiry",
            "expire",
            "medicine",
            "vaccine"
        ]

        # -----------------------------------
        # Procurement (highest priority)
        # -----------------------------------

        for word in procurement_keywords:
            if word in text:
                return IntentEngine.PROCUREMENT

        # -----------------------------------
        # Shipment
        # -----------------------------------

        for word in shipment_keywords:
            if word in text:
                return IntentEngine.SHIPMENT

        # -----------------------------------
        # Warehouse
        # -----------------------------------

        for word in warehouse_keywords:
            if word in text:
                return IntentEngine.WAREHOUSE

        # -----------------------------------
        # Inventory
        # -----------------------------------

        for word in inventory_keywords:
            if word in text:
                return IntentEngine.INVENTORY

        return IntentEngine.UNKNOWN