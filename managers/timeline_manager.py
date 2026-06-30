"""
backend/managers/timeline_manager.py

Handles story progression.

This manager is the ONLY place that should modify
called_timelines.
"""

from __future__ import annotations

from data.timelines import (
    TIMELINES,
    get as get_timeline,
    prerequisites as get_prerequisites,
)


class TimelineManager:

    def __init__(self, model):
        self.model = model

    # ==========================================================
    # Internal
    # ==========================================================

    @property
    def _list(self) -> list[str]:
        data = self.model.called_timelines

        if data is None:
            data = []
            self.model.called_timelines = data

        return data

    def _commit(self, timelines: list[str]) -> None:
        """
        Writes timelines back to the save.

        Removes duplicates while preserving order.
        """

        unique = []

        for t in timelines:
            if t not in unique:
                unique.append(t)

        self.model.called_timelines = unique

    # ==========================================================
    # Queries
    # ==========================================================

    def all(self) -> list[str]:
        return list(self._list)

    def count(self) -> int:
        return len(self._list)

    def exists(self, timeline: str) -> bool:
        return timeline in TIMELINES

    def unlocked(self, timeline: str) -> bool:
        return timeline in self._list

    def locked(self, timeline: str) -> bool:
        return timeline not in self._list

    # ==========================================================
    # Modification
    # ==========================================================

    def unlock(self, timeline: str) -> bool:

        if not self.exists(timeline):
            raise ValueError(f"Unknown timeline '{timeline}'")

        current = self._list

        if timeline in current:
            return False

        current.append(timeline)

        self._commit(current)

        return True

    def lock(self, timeline: str) -> bool:

        current = self._list

        if timeline not in current:
            return False

        current.remove(timeline)

        self._commit(current)

        return True

    def toggle(self, timeline: str):

        if self.unlocked(timeline):
            self.lock(timeline)
        else:
            self.unlock(timeline)

    def clear(self):

        self.model.called_timelines = []

    # ==========================================================
    # Bulk
    # ==========================================================

    def unlock_many(self, timelines):

        changed = False

        for timeline in timelines:
            changed |= self.unlock(timeline)

        return changed

    def lock_many(self, timelines):

        changed = False

        for timeline in timelines:
            changed |= self.lock(timeline)

        return changed

    # ==========================================================
    # Prerequisites
    # ==========================================================

    def prerequisites(self, timeline: str) -> list[str]:
        return get_prerequisites(timeline)

    def missing_prerequisites(self, timeline: str) -> list[str]:

        missing = []

        for prereq in self.prerequisites(timeline):

            if prereq not in self._list:
                missing.append(prereq)

        return missing

    def can_unlock(self, timeline: str) -> bool:

        return len(self.missing_prerequisites(timeline)) == 0

    # ==========================================================
    # Recursive unlock
    # ==========================================================

    def unlock_chain(self, timeline: str):
        """
        Unlock timeline and every prerequisite recursively.
        Ghost timelines (in prerequisites but not in our data) are
        added directly to called_timelines without a data check,
        so the chain never breaks on unknown entries.
        """
        visited: set[str] = set()
        order:   list[str] = []

        def dfs(name: str):
            if name in visited:
                return
            visited.add(name)
            for prereq in get_prerequisites(name):
                dfs(prereq)
            order.append(name)

        dfs(timeline)

        current = self._list
        changed = False
        for name in order:
            if name not in current:
                current.append(name)
                changed = True

        if changed:
            self._commit(current)

    # ==========================================================
    # Finish an entire story arc
    # ==========================================================

    def finish_story(self, story_name: str) -> dict:
        """
        Unlock every timeline in a story arc (with full prerequisite
        chains, including cross-arc dependencies and ghost timelines).

        Returns the max stat requirement per unlock_type found in the
        arc, e.g. {"enslavement": 55000.0, "coins": 0.0, "days": 27}.
        The caller is responsible for raising those stats — this
        manager only touches called_timelines.
        """
        from data.timelines import by_story

        timelines = by_story(story_name)
        if not timelines:
            return {}

        for tl in timelines:
            self.unlock_chain(tl.name)

        requirements: dict[str, float] = {
            "enslavement":       0.0,
            "coins":             0.0,
            "days":              0.0,
            "barony_documents":  0.0,
            "guild_documents":   0.0,
        }
        for tl in timelines:
            if tl.unlock_type in requirements:
                requirements[tl.unlock_type] = max(
                    requirements[tl.unlock_type], tl.unlock_value
                )

        return requirements

    # ==========================================================
    # Recursive dependency search
    # ==========================================================

    def dependents(self, timeline: str) -> list[str]:

        """
        Returns every timeline depending on this one.
        """

        result = []

        for candidate, info in TIMELINES.items():

            if timeline in info.prerequisites:
                result.append(candidate)

        return result

    def recursive_dependents(self, timeline: str):

        result = set()

        def dfs(name):

            for dep in self.dependents(name):

                if dep not in result:

                    result.add(dep)

                    dfs(dep)

        dfs(timeline)

        return sorted(result)

    # ==========================================================
    # Story groups
    # ==========================================================

    def by_story(self, story: str):

        return sorted(

            [
                t.name
                for t in TIMELINES.values()
                if t.story == story
            ],

            key=lambda n: TIMELINES[n].unlock_value
        )

    # ==========================================================
    # Progress
    # ==========================================================

    def completion_percent(self):

        if not TIMELINES:
            return 0.0

        return (
            len(self._list)
            / len(TIMELINES)
        ) * 100.0

    def remaining(self):

        return sorted(

            [
                t
                for t in TIMELINES
                if t not in self._list
            ]
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self):

        """
        Returns a list of progression issues.
        """

        issues = []

        for timeline in self._list:

            missing = self.missing_prerequisites(timeline)

            if missing:

                issues.append({

                    "timeline": timeline,

                    "missing": missing

                })

        return issues

    # ==========================================================
    # Python helpers
    # ==========================================================

    def __contains__(self, item):

        return self.unlocked(item)

    def __len__(self):

        return self.count()

    def __iter__(self):

        return iter(self._list)

    def __repr__(self):

        return (
            f"<TimelineManager "
            f"{self.count()}/{len(TIMELINES)} unlocked>"
        )