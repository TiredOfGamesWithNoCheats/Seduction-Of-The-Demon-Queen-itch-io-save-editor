"""
backend/data/poses.py

Known isometric poses.

This file contains ONLY static data.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Pose:
    id: str
    display_name: str


POSES = {

    "Domination":
        Pose(
            id="Domination",
            display_name="Domination",
        ),

    "Jerk-off":
        Pose(
            id="Jerk-off",
            display_name="Jerk Off",
        ),

    "Teasing":
        Pose(
            id="Teasing",
            display_name="Teasing",
        ),

    "Anilingus":
        Pose(
            id="Anilingus",
            display_name="Anilingus",
        ),

    "Dildo Blowjob":
        Pose(
            id="Dildo Blowjob",
            display_name="Dildo Blowjob",
        ),

    "Anal Toys":
        Pose(
            id="Anal Toys",
            display_name="Anal Toys",
        ),

    "Vaginal Cowgirl":
        Pose(
            id="Vaginal Cowgirl",
            display_name="Vaginal Cowgirl",
        ),

    "Legs Up":
        Pose(
            id="Legs Up",
            display_name="Legs Up",
        ),

    "Sex In The Gazebo":
        Pose(
            id="Sex In The Gazebo",
            display_name="Sex In The Gazebo",
        ),

    "Passion":
        Pose(
            id="Passion",
            display_name="Passion",
        ),
}


# --------------------------------------------------------
# Helper API
# --------------------------------------------------------

def get(pose_id: str) -> Pose | None:
    return POSES.get(pose_id)


def exists(pose_id: str) -> bool:
    return pose_id in POSES


def all() -> dict[str, Pose]:
    return POSES


def names() -> list[str]:
    return sorted(POSES.keys())


def display_names() -> list[str]:
    return sorted(
        pose.display_name
        for pose in POSES.values()
    )


def ids() -> list[str]:
    return list(POSES.keys())