"""
data/poses.py

Isometric pose database.

IDs must match exactly what SaveManager.add_pose() stores.
Confirmed from UpdateProgression.gd and SaveManager.gd defaults.
Dildo Blowjob and Anal Toys IDs are unconfirmed — marked below.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Pose:
    id:            str
    display_name:  str
    unlocked_by:   str = ""   # timeline that triggers add_pose()


# Insertion order = game's natural unlock order
POSES = {

    # Default poses (SaveManager.gd save_data defaults)
    "Domination":
        Pose(id="Domination",    display_name="Domination"),

    "Jerk-off":
        Pose(id="Jerk-off",      display_name="Jerk Off"),

    "Teasing":
        Pose(id="Teasing",       display_name="Teasing"),

    # Unlocked by timelines (UpdateProgression.gd — strings are exact)
    "Anilingus":
        Pose(id="Anilingus",     display_name="Anilingus",
             unlocked_by="SomethingNew"),

    "VaginalCowgirl":
        Pose(id="VaginalCowgirl", display_name="Vaginal Cowgirl",
             unlocked_by="Cowgirl"),

    "LegsUp":
        Pose(id="LegsUp",        display_name="Legs Up",
             unlocked_by="Footjob"),

    "SexInTheGazebo":
        Pose(id="SexInTheGazebo", display_name="Sex In The Gazebo",
             unlocked_by="FreeBird"),

    "Passion":
        Pose(id="Passion",       display_name="Passion",
             unlocked_by="PheromoneBomb"),

    # Unlocked by item purchases — confirmed from ShopUI.gd _on_dildo_purchased / _on_anal_toy_purchased
    "DildoBlowjob":
        Pose(id="DildoBlowjob",  display_name="Dildo Blowjob",
             unlocked_by="Dildo (item)"),

    "AnalToys":
        Pose(id="AnalToys",      display_name="Anal Toys",
             unlocked_by="AnalToy (item)"),
}


def get(pose_id: str) -> Pose | None:
    return POSES.get(pose_id)


def exists(pose_id: str) -> bool:
    return pose_id in POSES


def all() -> dict[str, Pose]:
    return POSES


def ids() -> list[str]:
    return list(POSES.keys())


def display_names() -> list[str]:
    return [p.display_name for p in POSES.values()]
