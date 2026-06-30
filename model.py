"""
model.py
Central save model — the only object the UI should talk to.
Managers are wired in after a save is loaded.
"""

from __future__ import annotations

from savefile import SaveFile
from managers.timeline_manager import TimelineManager
from managers.room_manager     import RoomManager
from managers.pose_manager     import PoseManager
from managers.item_manager     import ItemManager
from managers.stats_manager    import StatsManager
from managers.validation       import ValidationManager


class SaveModel:

    def __init__(self):
        self.save:      SaveFile | None = None
        self.filename:  str | None      = None

        # Managers — None until a save is loaded
        self.timelines: TimelineManager | None = None
        self.rooms:     RoomManager     | None = None
        self.poses:     PoseManager     | None = None
        self.items:     ItemManager     | None = None
        self.stats:     StatsManager    | None = None
        self.validator: ValidationManager | None = None

    # ----------------------------------------------------------
    # State
    # ----------------------------------------------------------

    @property
    def loaded(self) -> bool:
        return self.save is not None

    # ----------------------------------------------------------
    # File operations
    # ----------------------------------------------------------

    def load(self, filename: str):
        self.filename = filename
        self.save = SaveFile.load(filename)
        self._init_managers()

    def save_file(self):
        if not self.loaded:
            raise RuntimeError("No save loaded.")
        self.save.save()

    def save_as(self, filename: str):
        if not self.loaded:
            raise RuntimeError("No save loaded.")
        from godot_crypto import GodotCrypto
        GodotCrypto.save(filename, self.save.config.dumps().encode("utf-8"))

    # ----------------------------------------------------------
    # Manager wiring
    # ----------------------------------------------------------

    def _init_managers(self):
        self.timelines = TimelineManager(self)
        self.rooms     = RoomManager(self)
        self.poses     = PoseManager(self)
        self.items     = ItemManager(self)
        self.stats     = StatsManager(self)
        self.validator = ValidationManager(
            stats=self.stats,
            timelines=self.timelines,
            rooms=self.rooms,
            poses=self.poses,
            items=self.items,
        )

    # ----------------------------------------------------------
    # Low-level access (used by managers)
    # ----------------------------------------------------------

    @property
    def game(self) -> dict:
        if not self.loaded:
            raise RuntimeError("No save loaded.")
        return self.save.config.sections["GameState"]

    def get(self, key, default=None):
        return self.game.get(key, default)

    def set(self, key, value):
        self.game[key] = value

    def has(self, key) -> bool:
        return key in self.game

    # ----------------------------------------------------------
    # Convenience properties (used by managers)
    # ----------------------------------------------------------

    @property
    def called_timelines(self) -> list:
        val = self.get("called_timelines", [])
        return val if isinstance(val, list) else []

    @called_timelines.setter
    def called_timelines(self, value):
        self.set("called_timelines", list(value))

    @property
    def unlocked_rooms(self) -> list:
        val = self.get("unlocked_rooms", [])
        return val if isinstance(val, list) else []

    @unlocked_rooms.setter
    def unlocked_rooms(self, value):
        self.set("unlocked_rooms", list(value))

    @property
    def available_poses(self) -> list:
        val = self.get("available_isometric_poses", [])
        return val if isinstance(val, list) else []

    @available_poses.setter
    def available_poses(self, value):
        self.set("available_isometric_poses", list(value))

    @property
    def inventory(self) -> dict:
        val = self.get("inventory", {})
        return val if isinstance(val, dict) else {}

    @inventory.setter
    def inventory(self, value):
        self.set("inventory", dict(value))

    @property
    def purchased_items(self) -> list:
        val = self.get("purchased_items", [])
        return val if isinstance(val, list) else []

    @purchased_items.setter
    def purchased_items(self, value):
        self.set("purchased_items", list(value))
