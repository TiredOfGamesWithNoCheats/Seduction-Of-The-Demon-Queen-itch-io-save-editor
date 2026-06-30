"""
managers/stats_manager.py

Read/write player statistics from the save.
"""

from __future__ import annotations


# Must match ChangeTimeOfDay.gd StateTime enum: DAY=0, EVENING=1, NIGHT=2
TIME_OF_DAY_NAMES = ["Day", "Evening", "Night"]


class StatsManager:

    def __init__(self, model):
        self.model = model

    # ==========================================================
    # Currency
    # ==========================================================

    @property
    def coins(self) -> int:
        return int(self.model.get("coins", 0))

    @coins.setter
    def coins(self, value: int):
        self.model.set("coins", max(0, int(value)))

    @property
    def total_coins(self) -> int:
        return int(self.model.get("total_coins", 0))

    @total_coins.setter
    def total_coins(self, value: int):
        self.model.set("total_coins", max(0, int(value)))

    # ----------------------------------------------------------
    # Anti-cheat awareness
    # The game runs _detect_cheating() on load:
    #   max_total = easy*70 + normal*140 + hard*210
    #   if coins > max_total or total_coins > max_total → wipe + quit
    # ----------------------------------------------------------

    def anti_cheat_limit(self) -> int:
        """Max coins the game will tolerate before wiping the save."""
        return (
            self.easy_mode_completions   * 70
            + self.normal_mode_completions * 140
            + self.hard_mode_completions   * 210
        )

    def max_coins(self, amount: int = 999_999_999):
        """Set coins and total_coins. Does NOT touch completions."""
        self.coins       = amount
        self.total_coins = amount

    def bypass_anti_cheat(self, amount: int | None = None):
        """
        Raise hard_mode_completions enough to satisfy the anti-cheat
        check for the given amount (defaults to current coins).
        """
        if amount is None:
            amount = max(self.coins, self.total_coins)
        if self.anti_cheat_limit() < amount:
            self.hard_mode_completions = -(-amount // 210)  # ceiling div

    # ==========================================================
    # Enslavement
    # ==========================================================

    @property
    def enslavement(self) -> float:
        return float(self.model.get("enslavement", 0.0))

    @enslavement.setter
    def enslavement(self, value: float):
        self.model.set("enslavement", float(value))

    @property
    def enslavement_max_extra(self) -> list:
        return list(self.model.get("enslavement_max_extra", []))

    @enslavement_max_extra.setter
    def enslavement_max_extra(self, value: list):
        self.model.set("enslavement_max_extra", list(value))

    # UpdateProgression.gd: timeline -> enslavement_max_extra bonus key.
    # PheromoneBomb is the trigger, "GardenFun" is the bonus name it adds.
    ENSLAVEMENT_BONUS_MAP = {
        "SomethingNew":   "SomethingNew",
        "TestNewItem":    "TestNewItem",
        "Cowgirl":        "Cowgirl",
        "DepressedHero":  "DepressedHero",
        "ChangesInLife":  "ChangesInLife",
        "FreeBird":       "FreeBird",
        "PheromoneBomb":  "GardenFun",
        "JoyfulJailbird": "JoyfulJailbird",
        "Penance":        "Penance",
        "Blessing":       "Blessing",
        "Helen":          "Helen",
    }

    def sync_enslavement_max_extra(self, called_timelines):
        """
        Add enslavement_max_extra bonus entries for every timeline in
        called_timelines that grants one, mirroring UpdateProgression.gd.
        Only adds entries for timelines actually unlocked — does not
        blanket-add every known bonus.
        """
        called = set(called_timelines)
        current = list(self.model.get("enslavement_max_extra", []))
        changed = False
        for timeline, bonus_key in self.ENSLAVEMENT_BONUS_MAP.items():
            if timeline in called and bonus_key not in current:
                current.append(bonus_key)
                changed = True
        if changed:
            self.model.set("enslavement_max_extra", current)

    def max_enslavement(self, cap: float = 100_000.0):
        self.enslavement = cap
        # Blanket cheat — grant every known bonus regardless of timelines.
        current = list(self.model.get("enslavement_max_extra", []))
        for bonus_key in self.ENSLAVEMENT_BONUS_MAP.values():
            if bonus_key not in current:
                current.append(bonus_key)
        self.model.set("enslavement_max_extra", current)

    # ==========================================================
    # Time
    # ==========================================================

    @property
    def current_day(self) -> int:
        return int(self.model.get("current_day", 1))

    @current_day.setter
    def current_day(self, value: int):
        self.model.set("current_day", max(1, int(value)))

    @property
    def time_of_day(self) -> int:
        return int(self.model.get("time_of_day", 0))

    @time_of_day.setter
    def time_of_day(self, value: int):
        self.model.set("time_of_day", int(value) % len(TIME_OF_DAY_NAMES))

    @property
    def time_of_day_name(self) -> str:
        return TIME_OF_DAY_NAMES[self.time_of_day]

    @time_of_day_name.setter
    def time_of_day_name(self, name: str):
        idx = TIME_OF_DAY_NAMES.index(name)
        self.time_of_day = idx

    # ==========================================================
    # Climax counters
    # ==========================================================

    @property
    def total_c1_cummed(self) -> int:
        return int(self.model.get("total_c1_cummed", 0))

    @total_c1_cummed.setter
    def total_c1_cummed(self, value: int):
        self.model.set("total_c1_cummed", max(0, int(value)))

    @property
    def total_c2_cummed(self) -> int:
        return int(self.model.get("total_c2_cummed", 0))

    @total_c2_cummed.setter
    def total_c2_cummed(self, value: int):
        self.model.set("total_c2_cummed", max(0, int(value)))

    # ==========================================================
    # Isometric game
    # ==========================================================

    @property
    def is_first_isometric_game(self) -> bool:
        return bool(self.model.get("is_first_isometric_game", False))

    @is_first_isometric_game.setter
    def is_first_isometric_game(self, value: bool):
        self.model.set("is_first_isometric_game", bool(value))

    @property
    def has_played_isometric_today(self) -> bool:
        return bool(self.model.get("has_played_isometric_today", False))

    @has_played_isometric_today.setter
    def has_played_isometric_today(self, value: bool):
        self.model.set("has_played_isometric_today", bool(value))

    # ==========================================================
    # Session / launch
    # ==========================================================

    @property
    def launch_count(self) -> int:
        return int(self.model.get("launch_count", 0))

    @launch_count.setter
    def launch_count(self, value: int):
        self.model.set("launch_count", max(0, int(value)))

    @property
    def playtime_array(self) -> list:
        return list(self.model.get("playtime_array", [0, 0, 0, 0]))

    @playtime_array.setter
    def playtime_array(self, value: list):
        self.model.set("playtime_array", list(value))

    # ==========================================================
    # Completions
    # ==========================================================

    @property
    def easy_mode_completions(self) -> int:
        return int(self.model.get("easy_mode_completions", 0))

    @easy_mode_completions.setter
    def easy_mode_completions(self, value: int):
        self.model.set("easy_mode_completions", max(0, int(value)))

    @property
    def normal_mode_completions(self) -> int:
        return int(self.model.get("normal_mode_completions", 0))

    @normal_mode_completions.setter
    def normal_mode_completions(self, value: int):
        self.model.set("normal_mode_completions", max(0, int(value)))

    @property
    def hard_mode_completions(self) -> int:
        return int(self.model.get("hard_mode_completions", 0))

    @hard_mode_completions.setter
    def hard_mode_completions(self, value: int):
        self.model.set("hard_mode_completions", max(0, int(value)))

    @property
    def suppression_mini_game_total_completions(self) -> int:
        return int(self.model.get("suppression_mini_game_total_completions", 0))

    @suppression_mini_game_total_completions.setter
    def suppression_mini_game_total_completions(self, value: int):
        self.model.set("suppression_mini_game_total_completions", max(0, int(value)))

    @property
    def temptation_mini_game_total_completions(self) -> int:
        return int(self.model.get("temptation_mini_game_total_completions", 0))

    @temptation_mini_game_total_completions.setter
    def temptation_mini_game_total_completions(self, value: int):
        self.model.set("temptation_mini_game_total_completions", max(0, int(value)))

    # ==========================================================
    # Game state flags
    # ==========================================================

    @property
    def is_game_completed(self) -> bool:
        return bool(self.model.get("is_game_completed", False))

    @is_game_completed.setter
    def is_game_completed(self, value: bool):
        self.model.set("is_game_completed", bool(value))

    @property
    def is_new_game(self) -> bool:
        return bool(self.model.get("is_new_game", True))

    @is_new_game.setter
    def is_new_game(self, value: bool):
        self.model.set("is_new_game", bool(value))

    @property
    def door_lock(self) -> bool:
        return bool(self.model.get("door_lock", False))

    @door_lock.setter
    def door_lock(self, value: bool):
        self.model.set("door_lock", bool(value))

    @property
    def state_game(self) -> int:
        return int(self.model.get("state_game", 0))

    @state_game.setter
    def state_game(self, value: int):
        self.model.set("state_game", int(value))

    @property
    def game_version(self) -> str:
        return str(self.model.get("game_version", ""))

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self):

        issues = []

        if self.coins < 0:
            issues.append({"type": "negative_coins"})

        if self.total_coins < 0:
            issues.append({"type": "negative_total_coins"})

        if self.current_day < 1:
            issues.append({"type": "invalid_day", "value": self.current_day})

        if self.time_of_day not in range(len(TIME_OF_DAY_NAMES)):
            issues.append({"type": "invalid_time_of_day", "value": self.time_of_day})

        pt = self.playtime_array
        if len(pt) != 4:
            issues.append({"type": "invalid_playtime_array", "length": len(pt)})

        return issues

    # ==========================================================
    # Python helpers
    # ==========================================================

    def __repr__(self):
        return (
            f"<StatsManager "
            f"day={self.current_day} "
            f"coins={self.coins} "
            f"enslavement={self.enslavement:.0f}>"
        )
