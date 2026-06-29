"""
Room definitions for SOTDQ.

The game unlocks rooms from timelines.

This file intentionally contains no logic.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Room:

    id: str

    display_name: str

    default: bool = False

    unlocked_by: str | None = None


ROOMS = {

    "ThroneRoom":
        Room(
            id="ThroneRoom",
            display_name="Throne Room",
            default=True,
        ),

    "Bedroom":
        Room(
            id="Bedroom",
            display_name="Bedroom",
            default=True,
        ),

    "Shop":
        Room(
            id="Shop",
            display_name="Shop",
            unlocked_by="ArtOfVergil4",
        ),

    "Garden":
        Room(
            id="Garden",
            display_name="Garden",
            unlocked_by="FreeBird",
        ),

    "DoeRoom":
        Room(
            id="DoeRoom",
            display_name="Doe Room",
            unlocked_by="NewButler",
        ),

    "ChancelleryRoom":
        Room(
            id="ChancelleryRoom",
            display_name="Chancellery",
            unlocked_by="NewButler",
        ),

    "CorridorRoom":
        Room(
            id="CorridorRoom",
            display_name="Corridor",
            unlocked_by="NewButler",
        ),

    "Guild":
        Room(
            id="Guild",
            display_name="Guild",
            unlocked_by="NewAdministrator",
        ),

    "Tavern":
        Room(
            id="Tavern",
            display_name="Tavern",
            unlocked_by="NewAdministrator",
        ),
}


def get(room_id: str):

    return ROOMS.get(room_id)


def exists(room_id: str):

    return room_id in ROOMS


def names():

    return sorted(ROOMS)


def all():

    return ROOMS