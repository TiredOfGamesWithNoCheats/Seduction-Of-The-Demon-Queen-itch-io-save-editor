"""
managers/room_manager.py

Derives unlocked rooms from story progression.
Mirrors the game's own RoomManager.check_and_unlock_rooms() logic.
"""

from __future__ import annotations

from data.rooms import ROOMS, get as get_room


class RoomManager:

    def __init__(self, model):
        self.model = model

    # ==========================================================
    # Internal
    # ==========================================================

    @property
    def _rooms(self) -> list:

        data = self.model.unlocked_rooms

        if data is None:
            data = []
            self.model.unlocked_rooms = data

        return data

    def _commit(self, rooms: list):

        unique = []

        for r in rooms:
            if r not in unique:
                unique.append(r)

        self.model.unlocked_rooms = unique

    # ==========================================================
    # Queries
    # ==========================================================

    def all(self) -> list[str]:
        return list(self._rooms)

    def count(self) -> int:
        return len(self._rooms)

    def is_unlocked(self, room_id: str) -> bool:
        return room_id in self._rooms

    def is_locked(self, room_id: str) -> bool:
        return room_id not in self._rooms

    # ==========================================================
    # Rebuild from timelines (mirrors the game)
    # ==========================================================

    def rebuild(self):
        """
        Recompute unlocked_rooms from called_timelines.
        This replicates what RoomManager.check_and_unlock_rooms()
        does in the game — default rooms are always included,
        and timeline-gated rooms are added when their timeline
        is present in called_timelines.
        """

        timelines = set(self.model.called_timelines or [])

        result = []

        for room in ROOMS.values():

            if room.default:
                result.append(room.id)
                continue

            if room.unlocked_by and room.unlocked_by in timelines:
                result.append(room.id)

        self._commit(result)

    # ==========================================================
    # Manual overrides (advanced editor)
    # ==========================================================

    def unlock(self, room_id: str) -> bool:

        rooms = self._rooms

        if room_id in rooms:
            return False

        rooms.append(room_id)
        self._commit(rooms)

        return True

    def lock(self, room_id: str) -> bool:

        rooms = self._rooms

        if room_id not in rooms:
            return False

        rooms.remove(room_id)
        self._commit(rooms)

        return True

    def toggle(self, room_id: str):

        if self.is_unlocked(room_id):
            self.lock(room_id)
        else:
            self.unlock(room_id)

    def unlock_all(self):
        self._commit(list(ROOMS.keys()))

    def lock_all(self):
        self.model.unlocked_rooms = []

    # ==========================================================
    # Database helpers
    # ==========================================================

    def available(self):
        """Room objects that are currently unlocked."""
        return [
            get_room(r)
            for r in self._rooms
            if get_room(r) is not None
        ]

    def locked(self):
        """Room objects that are still locked."""
        return [
            room
            for room in ROOMS.values()
            if room.id not in self._rooms
        ]

    def unlocked_by(self, timeline: str) -> list[str]:
        """Which rooms would be unlocked by this timeline."""
        return [
            room.id
            for room in ROOMS.values()
            if room.unlocked_by == timeline
        ]

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self):

        issues = []

        for room_id in self._rooms:

            if room_id not in ROOMS:
                issues.append({
                    "type": "unknown_room",
                    "room": room_id,
                })

        return issues

    # ==========================================================
    # Python helpers
    # ==========================================================

    def __contains__(self, item):
        return self.is_unlocked(item)

    def __len__(self):
        return self.count()

    def __iter__(self):
        return iter(self._rooms)

    def __repr__(self):
        return (
            f"<RoomManager "
            f"{self.count()}/{len(ROOMS)} unlocked>"
        )
