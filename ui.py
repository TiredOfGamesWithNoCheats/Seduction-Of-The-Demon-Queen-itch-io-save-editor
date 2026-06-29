"""
ui.py
Complete save editor GUI — unified styling throughout.
"""

from __future__ import annotations

import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk

import customtkinter as ctk

from model import SaveModel
from data.timelines import TIMELINES, by_story
from data.rooms     import ROOMS
from data.poses     import POSES
from data.items     import ITEMS

# ──────────────────────────────────────────────
# Design tokens (change here, applies everywhere)
# ──────────────────────────────────────────────
SIDEBAR_W   = 190
ACCENT      = "#3B8ED0"

# Font sizes
SZ_TITLE   = 15
SZ_SECTION = 13
SZ_BODY    = 13
SZ_HINT    = 12

# Spacing
PAD        = 16      # horizontal padding for page content
ROW_PY     = 5       # vertical padding per form row
HDR_PY     = (12, 6) # (top, bottom) for page header

# Buttons — all pages use the same widths
BTN_W      = 110     # primary action
BTN_W_SM   = 95      # secondary / destructive

# Treeview
TREE_FONT  = ("Segoe UI", 13)
TREE_ROW_H = 30


# ──────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────

def _page_header(parent, title: str) -> ctk.CTkFrame:
    """Returns the header frame so callers can pack buttons into it."""
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=PAD, pady=HDR_PY)
    ctk.CTkLabel(
        bar, text=title,
        font=ctk.CTkFont(size=SZ_TITLE, weight="bold"),
        anchor="w",
    ).pack(side="left")
    return bar


def _hint(parent, text: str):
    ctk.CTkLabel(
        parent, text=text,
        text_color="gray60",
        font=ctk.CTkFont(size=SZ_HINT),
        anchor="w",
    ).pack(fill="x", padx=PAD, pady=(0, 6))


def _section(parent, text: str):
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=SZ_SECTION, weight="bold"),
        anchor="w",
    ).pack(fill="x", pady=(14, 2))
    ctk.CTkFrame(parent, height=1, fg_color="gray35").pack(fill="x", pady=(0, 6))


def _form_row(parent, label: str, label_w: int = 180) -> ctk.StringVar:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=ROW_PY)
    ctk.CTkLabel(
        row, text=label, anchor="w", width=label_w,
        font=ctk.CTkFont(size=SZ_BODY),
    ).pack(side="left")
    var = ctk.StringVar(value="0")
    ctk.CTkEntry(row, textvariable=var, font=ctk.CTkFont(size=SZ_BODY)).pack(
        side="left", fill="x", expand=True)
    return var


def _flag_row(parent, label: str) -> ctk.BooleanVar:
    var = ctk.BooleanVar()
    ctk.CTkCheckBox(
        parent, text=label, variable=var,
        font=ctk.CTkFont(size=SZ_BODY),
    ).pack(anchor="w", pady=ROW_PY)
    return var


def _primary_btn(parent, text, cmd) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=cmd, width=BTN_W)


def _secondary_btn(parent, text, cmd) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text, command=cmd, width=BTN_W_SM,
        fg_color="gray30", hover_color="gray40",
    )


# ──────────────────────────────────────────────
# Base page
# ──────────────────────────────────────────────

class _Page(ctk.CTkFrame):
    def __init__(self, parent, model: SaveModel):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.model = model
        self._build()

    def _build(self):  pass
    def refresh(self): pass
    def collect(self): pass


# ──────────────────────────────────────────────
# General
# ──────────────────────────────────────────────

class GeneralPage(_Page):

    def _build(self):
        _page_header(self, "General")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        _section(scroll, "Currency")
        self._coins     = _form_row(scroll, "Coins")
        self._tot_coins = _form_row(scroll, "Total Coins")

        _section(scroll, "Progression")
        self._enslave   = _form_row(scroll, "Enslavement")
        self._day       = _form_row(scroll, "Current Day")

        tod_row = ctk.CTkFrame(scroll, fg_color="transparent")
        tod_row.pack(fill="x", pady=ROW_PY)
        ctk.CTkLabel(
            tod_row, text="Time of Day", anchor="w", width=180,
            font=ctk.CTkFont(size=SZ_BODY),
        ).pack(side="left")
        self._time_menu = ctk.CTkOptionMenu(
            tod_row, values=["Morning", "Afternoon", "Night"],
            font=ctk.CTkFont(size=SZ_BODY),
        )
        self._time_menu.pack(side="left", fill="x", expand=True)

        _section(scroll, "Flags")
        self._completed = _flag_row(scroll, "Game Completed")
        self._new_game  = _flag_row(scroll, "Is New Game")
        self._door      = _flag_row(scroll, "Door Locked")

    def refresh(self):
        if not self.model.loaded:
            return
        s = self.model.stats
        self._coins.set(str(s.coins))
        self._tot_coins.set(str(s.total_coins))
        self._enslave.set(f"{s.enslavement:.2f}")
        self._day.set(str(s.current_day))
        self._time_menu.set(s.time_of_day_name)
        self._completed.set(s.is_game_completed)
        self._new_game.set(s.is_new_game)
        self._door.set(s.door_lock)

    def collect(self):
        if not self.model.loaded:
            return
        s = self.model.stats
        try:
            s.coins       = int(self._coins.get())
            s.total_coins = int(self._tot_coins.get())
            s.enslavement = float(self._enslave.get())
            s.current_day = int(self._day.get())
        except ValueError:
            pass
        s.time_of_day_name  = self._time_menu.get()
        s.is_game_completed = self._completed.get()
        s.is_new_game       = self._new_game.get()
        s.door_lock         = self._door.get()


# ──────────────────────────────────────────────
# Story (tree view)
# ──────────────────────────────────────────────

class StoryPage(_Page):

    def __init__(self, parent, model: SaveModel, on_rooms_changed=None):
        self._on_rooms_changed = on_rooms_changed
        super().__init__(parent, model)

    def _build(self):
        self._apply_tree_style()

        # Header
        hdr = _page_header(self, "Story")
        _secondary_btn(hdr, "Clear All", self._clear_all).pack(side="right", padx=(4, 0))
        _primary_btn(hdr,   "Unlock All", self._unlock_all).pack(side="right")

        # Search bar
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=PAD, pady=(0, 4))
        ctk.CTkLabel(
            search_row, text="Search:",
            font=ctk.CTkFont(size=SZ_BODY),
        ).pack(side="left", padx=(0, 8))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._build_tree())
        ctk.CTkEntry(
            search_row, textvariable=self._search_var,
            placeholder_text="Filter timelines…",
            font=ctk.CTkFont(size=SZ_BODY),
        ).pack(side="left", fill="x", expand=True)

        _hint(self, "Click to toggle  ·  Double-click to unlock entire prerequisite chain")

        # Tree
        frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=6)
        frame.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        vsb = ttk.Scrollbar(frame)
        vsb.pack(side="right", fill="y")

        self._tree = ttk.Treeview(
            frame,
            style="Story.Treeview",
            yscrollcommand=vsb.set,
            selectmode="browse",
            show="tree",
        )
        self._tree.pack(fill="both", expand=True, padx=2, pady=2)
        vsb.config(command=self._tree.yview)

        self._tree.bind("<ButtonRelease-1>",        self._on_click)
        self._tree.bind("<Double-ButtonRelease-1>", self._on_double_click)

        self._build_tree()

    @staticmethod
    def _apply_tree_style():
        s = ttk.Style()
        s.theme_use("default")
        s.configure(
            "Story.Treeview",
            background="#1e1e1e",
            foreground="#CCCCCC",
            fieldbackground="#1e1e1e",
            rowheight=TREE_ROW_H,
            borderwidth=0,
            indent=20,
            font=TREE_FONT,
        )
        s.map(
            "Story.Treeview",
            background=[("selected", "#2C5F8A")],
            foreground=[("selected", "white")],
        )

    def _build_tree(self):
        self._tree.delete(*self._tree.get_children())

        query    = self._search_var.get().lower().strip()
        unlocked = set(self.model.called_timelines if self.model.loaded else [])

        for story in ["Demoness", "Vergil", "Esther"]:
            story_tls = {tl.name: tl for tl in by_story(story)}

            visible = (
                {n for n in story_tls if query in n.lower()}
                if query else set(story_tls)
            )
            if not visible:
                continue

            # Within-story children map
            children: dict[str, list] = defaultdict(list)
            for name, tl in story_tls.items():
                for prereq in tl.prerequisites:
                    if prereq in story_tls:
                        children[prereq].append(name)
            for key in children:
                children[key].sort(key=lambda n: story_tls[n].unlock_value)

            roots = sorted(
                [n for n in story_tls
                 if not any(p in story_tls for p in story_tls[n].prerequisites)],
                key=lambda n: story_tls[n].unlock_value,
            )

            hdr = self._tree.insert(
                "", "end",
                iid=f"_hdr_{story}",
                text=f"  {story} Story",
                open=True,
                tags=("hdr",),
            )

            inserted: set[str] = set()

            def _insert(parent_iid: str, name: str):
                if name in inserted or name not in visible:
                    return
                inserted.add(name)

                tl    = story_tls[name]
                u     = name in unlocked
                icon  = "✓" if u else "☐"
                tag   = "ok" if u else "no"
                req   = (f"  [{tl.unlock_type} ≥ {tl.unlock_value:,}]"
                         if tl.unlock_value else "")
                cross = [p for p in tl.prerequisites if p not in story_tls]
                note  = f"  ← {', '.join(cross)}" if cross else ""

                self._tree.insert(
                    parent_iid, "end",
                    iid=name,
                    text=f"  {icon}  {name}{req}{note}",
                    open=True,
                    tags=(tag, "tl"),
                )
                for child in children.get(name, []):
                    _insert(name, child)

            if query:
                for name in sorted(visible, key=lambda n: story_tls[n].unlock_value):
                    _insert(hdr, name)
            else:
                for root in roots:
                    _insert(hdr, root)
                for name in sorted(story_tls, key=lambda n: story_tls[n].unlock_value):
                    _insert(hdr, name)

        self._tree.tag_configure(
            "hdr", foreground="#3B8ED0",
            font=(TREE_FONT[0], TREE_FONT[1], "bold"),
        )
        self._tree.tag_configure("ok", foreground="#2ECC71")
        self._tree.tag_configure("no", foreground="#6C757D")

    def _timeline_at(self, event) -> str | None:
        iid = self._tree.identify_row(event.y)
        if not iid or "tl" not in self._tree.item(iid, "tags"):
            return None
        return iid

    def _on_click(self, event):
        name = self._timeline_at(event)
        if not name or not self.model.loaded:
            return
        if self.model.timelines.unlocked(name):
            self.model.timelines.lock(name)
        else:
            try:
                self.model.timelines.unlock(name)
            except ValueError:
                pass
        self.model.rooms.rebuild()
        if self._on_rooms_changed:
            self._on_rooms_changed()
        self._build_tree()

    def _on_double_click(self, event):
        name = self._timeline_at(event)
        if not name or not self.model.loaded:
            return
        self.model.timelines.unlock_chain(name)
        self.model.rooms.rebuild()
        if self._on_rooms_changed:
            self._on_rooms_changed()
        self._build_tree()

    def _unlock_all(self):
        if not self.model.loaded:
            return
        for name in TIMELINES:
            try:
                self.model.timelines.unlock(name)
            except ValueError:
                pass
        self.model.rooms.rebuild()
        self._build_tree()
        if self._on_rooms_changed:
            self._on_rooms_changed()

    def _clear_all(self):
        if not self.model.loaded:
            return
        self.model.timelines.clear()
        self.model.rooms.rebuild()
        self._build_tree()
        if self._on_rooms_changed:
            self._on_rooms_changed()

    def refresh(self):
        self._build_tree()


# ──────────────────────────────────────────────
# Rooms
# ──────────────────────────────────────────────

class RoomsPage(_Page):

    def _build(self):
        hdr = _page_header(self, "Rooms")
        _secondary_btn(hdr, "Unlock All", self._unlock_all).pack(side="right", padx=(4, 0))
        _primary_btn(hdr, "Rebuild from Timelines", self._rebuild).pack(side="right")

        _hint(self, "'Rebuild' derives rooms from story progress — mirrors the game's own logic.")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        self._vars: dict[str, ctk.BooleanVar] = {}

        for room in ROOMS.values():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=ROW_PY)

            var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                row, text=room.display_name, variable=var, width=180,
                font=ctk.CTkFont(size=SZ_BODY),
                command=lambda rid=room.id, v=var: self._toggle(rid, v),
            ).pack(side="left")

            note = (
                "Default"
                if room.default
                else f"Unlocks via: {room.unlocked_by}"
                if room.unlocked_by
                else ""
            )
            if note:
                ctk.CTkLabel(
                    row, text=note,
                    text_color="gray60", font=ctk.CTkFont(size=SZ_HINT),
                ).pack(side="left", padx=10)

            self._vars[room.id] = var

    def _toggle(self, room_id: str, var: ctk.BooleanVar):
        if not self.model.loaded:
            return
        if var.get():
            self.model.rooms.unlock(room_id)
        else:
            self.model.rooms.lock(room_id)

    def _rebuild(self):
        if not self.model.loaded:
            return
        self.model.rooms.rebuild()
        self.refresh()
        messagebox.showinfo("Rebuilt", "Rooms rebuilt from story progress.")

    def _unlock_all(self):
        if not self.model.loaded:
            return
        self.model.rooms.unlock_all()
        self.refresh()

    def refresh(self):
        if not self.model.loaded:
            return
        unlocked = set(self.model.rooms.all())
        for room_id, var in self._vars.items():
            var.set(room_id in unlocked)


# ──────────────────────────────────────────────
# Poses
# ──────────────────────────────────────────────

class PosesPage(_Page):

    def _build(self):
        hdr = _page_header(self, "Isometric Poses")
        _secondary_btn(hdr, "Lock All",   self._lock_all).pack(side="right", padx=(4, 0))
        _primary_btn(hdr,   "Unlock All", self._unlock_all).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        self._vars: dict[str, ctk.BooleanVar] = {}

        for pose in POSES.values():
            var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                scroll, text=pose.display_name, variable=var,
                font=ctk.CTkFont(size=SZ_BODY),
                command=lambda pid=pose.id, v=var: self._toggle(pid, v),
            ).pack(anchor="w", pady=ROW_PY)
            self._vars[pose.id] = var

    def _toggle(self, pose_id: str, var: ctk.BooleanVar):
        if not self.model.loaded:
            return
        if var.get():
            self.model.poses.unlock(pose_id)
        else:
            self.model.poses.lock(pose_id)

    def _unlock_all(self):
        if not self.model.loaded:
            return
        self.model.poses.unlock_all()
        self.refresh()

    def _lock_all(self):
        if not self.model.loaded:
            return
        self.model.poses.lock_all()
        self.refresh()

    def refresh(self):
        if not self.model.loaded:
            return
        unlocked = set(self.model.poses.all())
        for pose_id, var in self._vars.items():
            var.set(pose_id in unlocked)


# ──────────────────────────────────────────────
# Inventory
# ──────────────────────────────────────────────

class InventoryPage(_Page):

    def _build(self):
        hdr = _page_header(self, "Inventory & Shop")
        _secondary_btn(hdr, "Clear All", self._clear_all).pack(side="right", padx=(4, 0))
        _primary_btn(hdr,   "Max All",   self._max_all).pack(side="right")

        # Column header strip
        col_hdr = ctk.CTkFrame(self, fg_color="gray20", height=32)
        col_hdr.pack(fill="x", padx=PAD)
        col_hdr.pack_propagate(False)
        for text, w in [("Item", 210), ("Type", 110), ("Price", 75), ("Qty / Owned", 130)]:
            ctk.CTkLabel(
                col_hdr, text=text, width=w, anchor="w",
                font=ctk.CTkFont(size=SZ_BODY, weight="bold"),
            ).pack(side="left", padx=8)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD, pady=(4, 8))

        self._qty_vars:   dict[str, ctk.StringVar]  = {}
        self._purch_vars: dict[str, ctk.BooleanVar] = {}

        for item in ITEMS.values():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=ROW_PY)

            ctk.CTkLabel(
                row, text=item.display_name, width=210, anchor="w",
                font=ctk.CTkFont(size=SZ_BODY),
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row,
                text="Consumable" if item.consumable else "Permanent",
                width=110, anchor="w",
                text_color="gray60", font=ctk.CTkFont(size=SZ_BODY),
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row, text=f"{item.price}g", width=75, anchor="w",
                font=ctk.CTkFont(size=SZ_BODY),
            ).pack(side="left", padx=8)

            if item.consumable:
                qty_var = ctk.StringVar(value="0")
                ctk.CTkEntry(
                    row, textvariable=qty_var, width=100,
                    font=ctk.CTkFont(size=SZ_BODY),
                ).pack(side="left", padx=8)
                self._qty_vars[item.id] = qty_var
            else:
                purch_var = ctk.BooleanVar()
                ctk.CTkCheckBox(
                    row, text="Purchased", variable=purch_var, width=120,
                    font=ctk.CTkFont(size=SZ_BODY),
                    command=lambda iid=item.id, v=purch_var: self._toggle_purch(iid, v),
                ).pack(side="left", padx=8)
                self._purch_vars[item.id] = purch_var

            if item.required_timeline:
                ctk.CTkLabel(
                    row, text=f"Requires: {item.required_timeline}",
                    text_color="gray50", font=ctk.CTkFont(size=SZ_HINT),
                ).pack(side="left", padx=4)

    def _toggle_purch(self, item_id: str, var: ctk.BooleanVar):
        if not self.model.loaded:
            return
        if var.get():
            self.model.items.purchase(item_id)
        else:
            self.model.items.unpurchase(item_id)

    def _max_all(self):
        if not self.model.loaded:
            return
        self.model.items.unlock_all_items()
        self.refresh()

    def _clear_all(self):
        if not self.model.loaded:
            return
        self.model.items.remove_all_items()
        self.refresh()

    def refresh(self):
        if not self.model.loaded:
            return
        for item_id, var in self._qty_vars.items():
            var.set(str(self.model.items.quantity(item_id)))
        for item_id, var in self._purch_vars.items():
            var.set(self.model.items.is_purchased(item_id))

    def collect(self):
        if not self.model.loaded:
            return
        for item_id, var in self._qty_vars.items():
            try:
                self.model.items.set_quantity(item_id, int(var.get()))
            except ValueError:
                pass


# ──────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────

class StatsPage(_Page):

    def _build(self):
        _page_header(self, "Statistics")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        _section(scroll, "Session")
        self._version  = _form_row(scroll, "Game Version")
        self._launch   = _form_row(scroll, "Launch Count")
        self._playtime = _form_row(scroll, "Playtime (raw)")

        # Make version and playtime read-only after build
        # (we can't easily make _form_row return the entry widget,
        # so just treat them as editable — they'll be overwritten on refresh)

        _section(scroll, "Minigame Completions")
        self._easy   = _form_row(scroll, "Easy Mode")
        self._normal = _form_row(scroll, "Normal Mode")
        self._hard   = _form_row(scroll, "Hard Mode")
        self._suppr  = _form_row(scroll, "Suppression Minigame")
        self._tempt  = _form_row(scroll, "Temptation Minigame")

        _section(scroll, "Intimacy Counters")
        self._c1 = _form_row(scroll, "Character 1 Climaxes")
        self._c2 = _form_row(scroll, "Character 2 Climaxes")

    def refresh(self):
        if not self.model.loaded:
            return
        s = self.model.stats
        self._version.set(s.game_version)
        self._launch.set(str(s.launch_count))
        self._playtime.set(str(s.playtime_array))
        self._easy.set(str(s.easy_mode_completions))
        self._normal.set(str(s.normal_mode_completions))
        self._hard.set(str(s.hard_mode_completions))
        self._suppr.set(str(s.suppression_mini_game_total_completions))
        self._tempt.set(str(s.temptation_mini_game_total_completions))
        self._c1.set(str(s.total_c1_cummed))
        self._c2.set(str(s.total_c2_cummed))

    def collect(self):
        if not self.model.loaded:
            return
        s = self.model.stats
        try:
            s.launch_count                            = int(self._launch.get())
            s.easy_mode_completions                   = int(self._easy.get())
            s.normal_mode_completions                 = int(self._normal.get())
            s.hard_mode_completions                   = int(self._hard.get())
            s.suppression_mini_game_total_completions = int(self._suppr.get())
            s.temptation_mini_game_total_completions  = int(self._tempt.get())
            s.total_c1_cummed                         = int(self._c1.get())
            s.total_c2_cummed                         = int(self._c2.get())
        except ValueError:
            pass


# ──────────────────────────────────────────────
# Advanced (raw key-value editor)
# ──────────────────────────────────────────────

class AdvancedPage(_Page):

    def _build(self):
        hdr = _page_header(self, "Raw Save Data")
        _primary_btn(hdr, "Refresh", self.refresh).pack(side="right")

        _hint(self, "Edit any key directly. Changes apply when you click Save.")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=PAD, pady=(0, 8))

        self._vars: dict[str, ctk.StringVar] = {}

    def refresh(self):
        if not self.model.loaded:
            return
        for w in self._scroll.winfo_children():
            w.destroy()
        self._vars.clear()

        for key, val in self.model.game.items():
            row = ctk.CTkFrame(self._scroll, fg_color="transparent")
            row.pack(fill="x", pady=ROW_PY)
            ctk.CTkLabel(
                row, text=key, width=260, anchor="w",
                font=ctk.CTkFont(size=SZ_BODY),
            ).pack(side="left")
            var = ctk.StringVar(value=str(val))
            ctk.CTkEntry(
                row, textvariable=var,
                font=ctk.CTkFont(size=SZ_BODY),
            ).pack(side="left", fill="x", expand=True)
            self._vars[key] = var

    def collect(self):
        if not self.model.loaded:
            return
        from config_parser import GodotConfig
        for key, var in self._vars.items():
            try:
                self.model.set(key, GodotConfig.parse_value(var.get()))
            except Exception:
                pass


# ──────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────

class SaveEditorGUI(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("SOTDQ Save Editor")
        self.geometry("1060x720")
        self.minsize(940, 620)

        self.model = SaveModel()
        self._pages:       dict[str, _Page]         = {}
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        self._build()
        self._navigate("general")

    # ── Layout ──────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_topbar()
        self._build_sidebar()
        self._build_content()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=52, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        self._file_label = ctk.CTkLabel(
            bar, text="No save loaded",
            anchor="w", text_color="gray60",
            font=ctk.CTkFont(size=SZ_BODY),
        )
        self._file_label.grid(row=0, column=0, padx=14, sticky="ew")

        for col, (text, cmd) in enumerate(
            [("Open", self._open), ("Save", self._save), ("Backup", self._backup)],
            start=1,
        ):
            ctk.CTkButton(
                bar, text=text, width=90, command=cmd,
                font=ctk.CTkFont(size=SZ_BODY),
            ).grid(row=0, column=col, padx=4, pady=10)

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=SIDEBAR_W, corner_radius=0)
        sb.grid(row=1, column=0, sticky="ns")
        sb.grid_propagate(False)

        ctk.CTkLabel(
            sb, text="SOTDQ\nSave Editor",
            font=ctk.CTkFont(size=SZ_SECTION, weight="bold"),
            justify="center",
        ).pack(pady=(18, 6), padx=8)

        ctk.CTkFrame(sb, height=1, fg_color="gray30").pack(fill="x", padx=8, pady=4)

        for page_id, label in [
            ("general",   "General"),
            ("story",     "Story"),
            ("rooms",     "Rooms"),
            ("poses",     "Poses"),
            ("inventory", "Inventory"),
            ("stats",     "Statistics"),
            ("advanced",  "Advanced"),
        ]:
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                width=SIDEBAR_W - 16,
                font=ctk.CTkFont(size=SZ_BODY),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda p=page_id: self._navigate(p),
            )
            btn.pack(pady=2, padx=8)
            self._nav_buttons[page_id] = btn

        ctk.CTkFrame(sb, height=1, fg_color="gray30").pack(fill="x", padx=8, pady=(16, 4))
        ctk.CTkLabel(
            sb, text="Quick Cheats",
            text_color="gray60", font=ctk.CTkFont(size=SZ_HINT),
        ).pack(pady=(0, 4))

        for text, cmd, fg, hv in [
            ("Unlock Everything", self._cheat_unlock_all, "#5B2C6F", "#7D3C98"),
            ("Max Coins",         self._cheat_max_coins,  "#1A5276", "#2874A6"),
            ("Validate Save",     self._validate,         "gray30",  "gray40"),
        ]:
            ctk.CTkButton(
                sb, text=text, command=cmd,
                width=SIDEBAR_W - 16,
                font=ctk.CTkFont(size=SZ_BODY),
                fg_color=fg, hover_color=hv,
            ).pack(pady=2, padx=8)

    def _build_content(self):
        content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        content.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        story = StoryPage(
            content, self.model,
            on_rooms_changed=lambda: self._pages["rooms"].refresh(),
        )
        story.grid(row=0, column=0, sticky="nsew")
        self._pages["story"] = story

        for page_id, cls in [
            ("general",   GeneralPage),
            ("rooms",     RoomsPage),
            ("poses",     PosesPage),
            ("inventory", InventoryPage),
            ("stats",     StatsPage),
            ("advanced",  AdvancedPage),
        ]:
            page = cls(content, self.model)
            page.grid(row=0, column=0, sticky="nsew")
            self._pages[page_id] = page

    # ── Navigation ──────────────────────────────

    def _navigate(self, page_id: str):
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=ACCENT, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self._pages[page_id].tkraise()

    # ── File operations ──────────────────────────

    def _open(self):
        path = filedialog.askopenfilename(
            title="Open Save File",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            self.model.load(path)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to open save:\n{exc}")
            return
        self._file_label.configure(text=Path(path).name, text_color="white")
        self._refresh_all()

    def _save(self):
        if not self.model.loaded:
            messagebox.showwarning("No Save", "Open a save file first.")
            return
        for page in self._pages.values():
            page.collect()
        try:
            self.model.save_file()
            messagebox.showinfo("Saved", "Save written successfully.")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save:\n{exc}")

    def _backup(self):
        if not self.model.loaded:
            messagebox.showwarning("No Save", "Open a save file first.")
            return
        src = Path(self.model.filename)
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = src.parent / f"{src.stem}.bak_{ts}{src.suffix}"
        shutil.copy2(src, dst)
        messagebox.showinfo("Backup", f"Backup created:\n{dst.name}")

    def _refresh_all(self):
        for page in self._pages.values():
            page.refresh()

    # ── Cheats ──────────────────────────────────

    def _cheat_max_coins(self):
        if not self.model.loaded:
            messagebox.showwarning("No Save", "Open a save file first.")
            return
        amount = 999_999_999
        self.model.stats.max_coins(amount)
        self._pages["general"].refresh()
        self._offer_bypass(amount)

    def _cheat_unlock_all(self):
        if not self.model.loaded:
            messagebox.showwarning("No Save", "Open a save file first.")
            return
        for name in TIMELINES:
            try:
                self.model.timelines.unlock(name)
            except Exception:
                pass
        self.model.rooms.rebuild()
        self.model.poses.unlock_all()
        amount = 999_999_999
        self.model.stats.max_coins(amount)
        self.model.stats.max_enslavement()
        self.model.items.unlock_all_items()
        self._refresh_all()
        self._offer_bypass(amount)

    def _offer_bypass(self, amount: int):
        """
        If the current coin amount exceeds the anti-cheat limit,
        warn the player and offer to bypass it.
        """
        limit = self.model.stats.anti_cheat_limit()
        if amount <= limit:
            return

        want_bypass = messagebox.askyesno(
            "Anti-Cheat Warning",
            f"Coins set to {amount:,}.\n\n"
            f"⚠  The game has an anti-cheat check:\n"
            f"      limit = easy×70 + normal×140 + hard×210\n"
            f"      your limit = {limit:,}\n\n"
            f"If you load this save in-game, it will detect the discrepancy,\n"
            f"wipe your coins and inventory, and close itself.\n\n"
            f"We can bypass this by inflating your hard-mode completion\n"
            f"count to a value that satisfies the formula.\n\n"
            f"Bypass the anti-cheat?",
            icon="warning",
        )
        if want_bypass:
            self.model.stats.bypass_anti_cheat(amount)
            self._pages["stats"].refresh()

    def _validate(self):
        if not self.model.loaded:
            messagebox.showwarning("No Save", "Open a save file first.")
            return
        report = self.model.validator.run()
        if report["ok"]:
            messagebox.showinfo("Validate", "No issues found — save looks valid.")
        else:
            lines = [f"{len(report['issues'])} issue(s) found:\n"]
            for issue in report["issues"]:
                src    = issue.get("source", "?")
                detail = issue.get("detail") or issue.get("type", "?")
                lines.append(f"  [{src}]  {detail}")
            messagebox.showwarning("Validate", "\n".join(lines))
