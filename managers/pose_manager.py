"""
managers/pose_manager.py

Handles unlocked isometric poses.
"""

from __future__ import annotations

from data.poses import POSES, get as get_pose


class PoseManager:

    def __init__(self, model):
        self.model = model

    # ==========================================================
    # Internal
    # ==========================================================

    @property
    def _poses(self) -> list:

        poses = self.model.available_poses

        if poses is None:
            poses = []
            self.model.available_poses = poses

        return poses

    def _commit(self, poses: list):

        unique = []

        for pose in poses:
            if pose not in unique:
                unique.append(pose)

        self.model.available_poses = unique

    # ==========================================================
    # Queries
    # ==========================================================

    def all(self) -> list[str]:
        return list(self._poses)

    def count(self) -> int:
        return len(self._poses)

    def exists(self, pose_id: str) -> bool:
        return pose_id in POSES

    def is_unlocked(self, pose_id: str) -> bool:
        return pose_id in self._poses

    def is_locked(self, pose_id: str) -> bool:
        return pose_id not in self._poses

    # ==========================================================
    # Modification
    # ==========================================================

    def unlock(self, pose_id: str) -> bool:

        if not self.exists(pose_id):
            raise ValueError(f"Unknown pose '{pose_id}'")

        poses = self._poses

        if pose_id in poses:
            return False

        poses.append(pose_id)
        self._commit(poses)

        return True

    def lock(self, pose_id: str) -> bool:

        poses = self._poses

        if pose_id not in poses:
            return False

        poses.remove(pose_id)
        self._commit(poses)

        return True

    def toggle(self, pose_id: str):

        if self.is_unlocked(pose_id):
            self.lock(pose_id)
        else:
            self.unlock(pose_id)

    def clear(self):
        self.model.available_poses = []

    # ==========================================================
    # Bulk
    # ==========================================================

    def unlock_all(self):
        self._commit(list(POSES.keys()))

    def lock_all(self):
        self.model.available_poses = []

    # ==========================================================
    # Database helpers
    # ==========================================================

    def available(self):
        """Pose objects that are currently unlocked."""
        return [
            get_pose(p)
            for p in self._poses
            if get_pose(p) is not None
        ]

    def locked(self):
        """Pose objects that are still locked."""
        return [
            pose
            for pose in POSES.values()
            if pose.id not in self._poses
        ]

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self):

        issues = []
        seen = set()

        for pose_id in self._poses:

            if pose_id in seen:
                issues.append({
                    "type": "duplicate_pose",
                    "pose": pose_id,
                })

            seen.add(pose_id)

            if pose_id not in POSES:
                issues.append({
                    "type": "unknown_pose",
                    "pose": pose_id,
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
        return iter(self._poses)

    def __repr__(self):
        return (
            f"<PoseManager "
            f"{self.count()}/{len(POSES)} unlocked>"
        )
