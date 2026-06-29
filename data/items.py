"""
backend/data/items.py

Static item database for SOTDQ.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Item:
    id: str
    display_name: str
    description_key: str
    name_key: str

    price: int

    consumable: bool

    max_quantity: int

    infinite_stock: bool

    required_timeline: str | None

    purchase_effect: str | None

    shop_type: str

    icon: str


ITEMS = {

    "Igniter":
        Item(
            id="Igniter",
            display_name="Igniter",
            name_key="ItemNameIgniter",
            description_key="ItemDescriptionIgniter",
            price=60,
            consumable=True,
            max_quantity=999,
            infinite_stock=True,
            required_timeline=None,
            purchase_effect=None,
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/4_icon.jpg",
        ),

    "Tonic":
        Item(
            id="Tonic",
            display_name="Tonic",
            name_key="ItemNameTonic",
            description_key="ItemDescriptionTonic",
            price=30,
            consumable=True,
            max_quantity=999,
            infinite_stock=True,
            required_timeline=None,
            purchase_effect=None,
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/3_icon.jpg",
        ),

    "Essence of craving":
        Item(
            id="Essence of craving",
            display_name="Essence of craving",
            name_key="ItemNameEssenceOfCraving",
            description_key="ItemDescriptionEssenceOfCraving",
            price=10,
            consumable=True,
            max_quantity=999,
            infinite_stock=True,
            required_timeline=None,
            purchase_effect=None,
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/2_icon.jpg",
        ),

    "Aphrodisiac":
        Item(
            id="Aphrodisiac",
            display_name="Aphrodisiac",
            name_key="ItemNameAphrodisiac",
            description_key="ItemDescriptionAphrodisiac",
            price=10,
            consumable=True,
            max_quantity=999,
            infinite_stock=True,
            required_timeline=None,
            purchase_effect=None,
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/1_icon.jpg",
        ),

    "Dildo":
        Item(
            id="Dildo",
            display_name="Dildo",
            name_key="ItemNameDildo",
            description_key="ItemDescriptionDildo",
            price=200,
            consumable=False,
            max_quantity=1,
            infinite_stock=False,
            required_timeline="BehindTavern",
            purchase_effect="_on_dildo_purchased",
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/5_icon.jpg",
        ),

    "GoblinSlayerHelmet":
        Item(
            id="GoblinSlayerHelmet",
            display_name="Goblin Slayer Helmet",
            name_key="ItemNameHelmetGoblinDestroyer",
            description_key="ItemDescriptionHelmetGoblinDestroyer",
            price=150,
            consumable=False,
            max_quantity=1,
            infinite_stock=False,
            required_timeline=None,
            purchase_effect=None,
            shop_type="MadmanShopUI",
            icon="res://assets/ui/item_icons/6_icon.jpg",
        ),

    "LegExoskeleton":
        Item(
            id="LegExoskeleton",
            display_name="Leg Exoskeleton",
            name_key="ItemNameExoskeletonLegs",
            description_key="ItemDescriptionExoskeletonLegs",
            price=300,
            consumable=False,
            max_quantity=1,
            infinite_stock=False,
            required_timeline=None,
            purchase_effect=None,
            shop_type="MadmanShopUI",
            icon="res://assets/ui/item_icons/7_icon.jpg",
        ),

    "TorsoExoskeleton":
        Item(
            id="TorsoExoskeleton",
            display_name="Torso Exoskeleton",
            name_key="ItemNameExoskeletonBody",
            description_key="ItemDescriptionExoskeletonBody",
            price=350,
            consumable=False,
            max_quantity=1,
            infinite_stock=False,
            required_timeline=None,
            purchase_effect=None,
            shop_type="MadmanShopUI",
            icon="res://assets/ui/item_icons/8_icon.jpg",
        ),

    "AnalToy":
        Item(
            id="AnalToy",
            display_name="Anal Toy",
            name_key="ItemNameAnalToy",
            description_key="ItemDescriptionAnalToy",
            price=300,
            consumable=False,
            max_quantity=1,
            infinite_stock=False,
            required_timeline="BloodDraw",
            purchase_effect="_on_anal_toy_purchased",
            shop_type="ShopUI",
            icon="res://assets/ui/item_icons/9_icon.jpg",
        ),
}


def get(item_id: str) -> Item | None:
    return ITEMS.get(item_id)


def exists(item_id: str) -> bool:
    return item_id in ITEMS


def all() -> dict[str, Item]:
    return ITEMS


def names() -> list[str]:
    return sorted(ITEMS.keys())


def shop(shop_type: str) -> list[Item]:
    return [
        item
        for item in ITEMS.values()
        if item.shop_type in (shop_type, "Both")
    ]


def unlocked(called_timelines: list[str]) -> list[Item]:
    """
    Return all items available with the current story progress.
    """
    available = []

    for item in ITEMS.values():

        if not item.required_timeline:
            available.append(item)
            continue

        if item.required_timeline in called_timelines:
            available.append(item)

    return available