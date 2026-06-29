"""
backend/managers/item_manager.py

Handles inventory, purchased items and shop stock.
"""

from __future__ import annotations

from data.items import ITEMS, get as get_item


class ItemManager:

    def __init__(self, model):
        self.model = model

    # ==========================================================
    # Internal helpers
    # ==========================================================

    @property
    def inventory(self) -> dict:

        data = self.model.inventory

        if data is None:
            data = {}
            self.model.inventory = data

        return data

    @property
    def purchased(self) -> list:

        data = self.model.purchased_items

        if data is None:
            data = []
            self.model.purchased_items = data

        return data

    @property
    def quantities(self) -> dict:

        data = self.model.get("shop_items_quantity", {})

        if data is None:
            data = {}
            self.model.set("shop_items_quantity", data)

        return data

    # ==========================================================
    # Inventory
    # ==========================================================

    def has(self, item_id: str) -> bool:
        return item_id in self.inventory

    def quantity(self, item_id: str) -> int:
        return int(self.inventory.get(item_id, 0))

    def set_quantity(self, item_id: str, amount: int):

        if amount <= 0:
            self.inventory.pop(item_id, None)
        else:
            self.inventory[item_id] = int(amount)

        self.model.inventory = dict(self.inventory)

    def add(self, item_id: str, amount: int = 1):

        self.set_quantity(
            item_id,
            self.quantity(item_id) + amount
        )

    def remove(self, item_id: str, amount: int = 1):

        self.set_quantity(
            item_id,
            self.quantity(item_id) - amount
        )

    def clear_inventory(self):

        self.model.inventory = {}

    # ==========================================================
    # Purchased items
    # ==========================================================

    def is_purchased(self, item_id: str) -> bool:

        return item_id in self.purchased

    def purchase(self, item_id: str):

        if item_id not in self.purchased:

            purchased = list(self.purchased)
            purchased.append(item_id)

            self.model.purchased_items = purchased

    def unpurchase(self, item_id: str):

        if item_id in self.purchased:

            purchased = list(self.purchased)
            purchased.remove(item_id)

            self.model.purchased_items = purchased

    def toggle_purchase(self, item_id: str):

        if self.is_purchased(item_id):
            self.unpurchase(item_id)
        else:
            self.purchase(item_id)

    def clear_purchases(self):

        self.model.purchased_items = []

    # ==========================================================
    # Shop quantities
    # ==========================================================

    def stock(self, item_id: str) -> int:

        return int(
            self.quantities.get(item_id, 0)
        )

    def set_stock(self, item_id: str, amount: int):

        stock = dict(self.quantities)

        stock[item_id] = max(0, int(amount))

        self.model.set(
            "shop_items_quantity",
            stock
        )

    def reset_stock(self):

        self.model.set(
            "shop_items_quantity",
            {}
        )

    # ==========================================================
    # Database helpers
    # ==========================================================

    def exists(self, item_id: str) -> bool:

        return item_id in ITEMS

    def get(self, item_id: str):

        return get_item(item_id)

    def all(self):

        return list(ITEMS.values())

    def available(self):

        """
        Items available based on unlocked timelines.
        """

        timelines = self.model.called_timelines

        available = []

        for item in ITEMS.values():

            if not item.required_timeline:
                available.append(item)
                continue

            if item.required_timeline in timelines:
                available.append(item)

        return available

    def locked(self):

        timelines = self.model.called_timelines

        locked = []

        for item in ITEMS.values():

            if item.required_timeline and \
               item.required_timeline not in timelines:

                locked.append(item)

        return locked

    # ==========================================================
    # Bulk helpers
    # ==========================================================

    def unlock_all_items(self):

        purchased = []

        inventory = {}

        for item in ITEMS.values():

            purchased.append(item.id)

            if item.consumable:
                inventory[item.id] = item.max_quantity
            else:
                inventory[item.id] = 1

        self.model.inventory = inventory
        self.model.purchased_items = purchased

    def remove_all_items(self):

        self.model.inventory = {}
        self.model.purchased_items = []

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self):

        issues = []

        for item_id, amount in self.inventory.items():

            item = get_item(item_id)

            if item is None:

                issues.append({
                    "type": "unknown_item",
                    "item": item_id
                })

                continue

            if amount < 0:

                issues.append({
                    "type": "negative_quantity",
                    "item": item_id
                })

            if amount > item.max_quantity:

                issues.append({
                    "type": "too_many_items",
                    "item": item_id,
                    "quantity": amount,
                    "maximum": item.max_quantity
                })

        return issues

    # ==========================================================
    # Python helpers
    # ==========================================================

    def __contains__(self, item):

        return self.has(item)

    def __len__(self):

        return len(self.inventory)

    def __repr__(self):

        return (
            f"<ItemManager "
            f"{len(self.inventory)} inventory items, "
            f"{len(self.purchased)} purchased>"
        )