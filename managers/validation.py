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
