"""
managers/validation.py

Runs all manager validators and returns a combined report.
"""

from __future__ import annotations


class ValidationManager:

    def __init__(
        self,
        stats=None,
        timelines=None,
        rooms=None,
        poses=None,
        items=None,
    ):
        self.stats = stats
        self.timelines = timelines
        self.rooms = rooms
        self.poses = poses
        self.items = items

    def _check_anti_cheat(self) -> list:
        """
        Replicates the game's _detect_cheating() logic.
        max_total = easy*70 + normal*140 + hard*210
        Flags if coins or total_coins exceed that limit.
        """
        if self.stats is None:
            return []

        limit       = self.stats.anti_cheat_limit()
        coins       = self.stats.coins
        total_coins = self.stats.total_coins
        issues      = []

        FIX = "Use 'Bypass Anti-Cheat' to fix."

        if coins > total_coins:
            issues.append({
                "type":   "anti_cheat_coins_exceed_total",
                "detail": f"coins ({coins:,}) > total_coins ({total_coins:,}) — game will wipe save on load. {FIX}",
            })

        if total_coins > limit:
            issues.append({
                "type":   "anti_cheat_total_coins_exceed_limit",
                "detail": f"total_coins ({total_coins:,}) exceeds limit ({limit:,}) — game will wipe save on load. {FIX}",
            })

        if coins > limit:
            issues.append({
                "type":   "anti_cheat_coins_exceed_limit",
                "detail": f"coins ({coins:,}) exceeds limit ({limit:,}) — game will wipe save on load. {FIX}",
            })

        return issues

    def _check_door_lock(self) -> list:
        """
        door_lock=true is only valid between SuddenEscape (which triggers
        the lock) and Penance (which releases it). Anything outside that
        window is a soft-lock or a skipped story segment.
        """
        if self.stats is None or self.timelines is None:
            return []

        locked   = self.stats.door_lock
        called   = set(self.timelines.all())
        issues   = []

        # SaveManager._repair_locked_timeline_side_effects() AUTO-ENABLES door_lock
        # on every load if SuddenEscape/BingeParty/Footjob is present without Penance.
        trigger_timelines = {"SuddenEscape", "BingeParty", "Footjob"}
        will_auto_lock = bool(trigger_timelines & called) and "Penance" not in called

        if not locked and will_auto_lock:
            issues.append({
                "type":   "door_lock_will_auto_enable",
                "detail": (
                    f"Door Locked is off, but the game will automatically "
                    f"re-enable it on load because "
                    f"{', '.join(trigger_timelines & called)} "
                    f"is in your timeline without Penance completing it. "
                    f"Either enable Door Locked here or unlock up to Penance."
                ),
            })

        if locked and "SuddenEscape" not in called:
            issues.append({
                "type":   "door_lock_missing_prerequisite",
                "detail": (
                    "Door is locked but SuddenEscape has not been completed. "
                    "All map areas will be disabled with no way to progress. "
                    "Complete SuddenEscape or disable Door Locked."
                ),
            })

        if locked and "Penance" in called:
            issues.append({
                "type":   "door_lock_already_resolved",
                "detail": (
                    "Door is locked but Penance is already completed. "
                    "The game should have unlocked the door after Penance. "
                    "Disable Door Locked to restore normal map access."
                ),
            })

        return issues

    def run(self) -> dict:
        """
        Run every available validator and return a combined report.

        Returns
        -------
        {
            "ok": bool,
            "issues": [
                {"source": "stats",     ...},
                {"source": "timelines", ...},
                ...
            ]
        }
        """

        all_issues = []

        for issue in self._check_anti_cheat():
            issue["source"] = "anti_cheat"
            all_issues.append(issue)

        for issue in self._check_door_lock():
            issue["source"] = "door_lock"
            all_issues.append(issue)

        for source, manager in [
            ("stats",     self.stats),
            ("timelines", self.timelines),
            ("rooms",     self.rooms),
            ("poses",     self.poses),
            ("items",     self.items),
        ]:
            if manager is None:
                continue

            try:
                issues = manager.validate()
            except Exception as exc:
                all_issues.append({
                    "source": source,
                    "type":   "validator_error",
                    "error":  str(exc),
                })
                continue

            for issue in issues:
                issue["source"] = source
                all_issues.append(issue)

        return {
            "ok":     len(all_issues) == 0,
            "issues": all_issues,
        }

    def summary(self) -> str:

        report = self.run()

        if report["ok"]:
            return "Save looks valid — no issues found."

        lines = [f"{len(report['issues'])} issue(s) found:"]

        for issue in report["issues"]:
            source = issue.get("source", "?")
            kind   = issue.get("type",   "?")
            lines.append(f"  [{source}] {kind}")

        return "\n".join(lines)
