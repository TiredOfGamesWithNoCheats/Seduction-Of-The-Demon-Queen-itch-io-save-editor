"""
backend/data/timelines.py

Timeline database for SOTDQ.

Contains ONLY static data.

No game logic should exist here.
"""

from dataclasses import dataclass, field


# ============================================================
# Timeline model
# ============================================================

@dataclass(slots=True)
class Timeline:

    name: str

    story: str

    unlock_type: str

    unlock_value: int | float

    prerequisites: list[str] = field(default_factory=list)

    required_items: list[str] = field(default_factory=list)

    unlock_rooms: list[str] = field(default_factory=list)


# ============================================================
# Room unlocks
# ============================================================

ROOM_UNLOCKS = {

    "ArtOfVergil4": [
        "Shop"
    ],

    "FreeBird": [
        "Garden"
    ],

    "NewButler": [
        "DoeRoom",
        "ChancelleryRoom",
        "CorridorRoom"
    ],

    "NewAdministrator": [
        "Guild",
        "Tavern"
    ],
}


# ============================================================
# Prerequisites
# ============================================================

TIMELINE_PREREQUISITES = {

    "RoomTour": ["ChibiStory"],
    "ConspiracyWithKasra": ["RoomTour"],
    "ImpJokes": ["ConspiracyWithKasra"],
    "ArtOfVergil3": ["ArtOfVergil2"],
    "SomethingNew": ["ArtOfVergil4"],
    "TableFap": ["SolidVergil"],
    "VergilSnake": ["TableFap"],
    "StarrySky": ["Tavern"],
    "PathOfDao": ["Hamsterdig"],
    "SimilarityToTheHero": ["BestHero"],
    "TestNewItem": ["TableFap"],
    "GoblinDestroyer": ["TestNewItem"],
    "MemoriesOfPose": ["TestNewItem"],
    "InsideTavern": ["MemoriesOfPose"],
    "BehindTavern": ["InsideTavern"],
    "PainfulThoughts": ["BehindTavern"],
    "SomethingNew2": ["PainfulThoughts"],
    "Cowgirl": ["SomethingNew2"],
    "GoblinDestroyer2": ["GoblinDestroyer"],
    "FamilyQuarrels": ["GoblinDestroyer2"],
    "ProblemsOfAcolytes": ["Cowgirl"],
    "DepressedHero": ["GoblinDestroyer"],
    "MadmanAndVergil": ["FamilyQuarrels"],
    "SomethingNew3": ["DepressedHero"],
    "TestNewItem2": ["SomethingNew3"],
    "Mira": ["MadmanAndVergil"],
    "TownSearch": ["TestNewItem2"],
    "TeachingOfSurvival": ["Mira"],
    "ChangesInLife": ["TownSearch"],
    "Palmistry": ["TeachingOfSurvival"],
    "MadmanAndVergil2": ["Palmistry"],
    "EstherAndVergil": ["MadmanAndVergil2"],
    "BaiXiAndVergil": ["EstherAndVergil"],
    "AndroidAndVergil": ["BaiXiAndVergil"],
    "BloodDraw": ["AndroidAndVergil"],
    "TeachingOfSurvival2": ["BloodDraw"],
    "СheeringUp": ["Cowgirl"],
    "FreeBird": ["СheeringUp"],
    "EstherAndVergil2": ["TeachingOfSurvival2"],
    "MinstrelProblem": ["EstherAndVergil2"],
    "RobberyOfAristocrats": ["MinstrelProblem"],
    "MinstrelProblem2": ["RobberyOfAristocrats"],
    "StrangePills": ["MinstrelProblem2"],
    "ProblemsOfAcolytes2": ["StrangePills"],
    "TwiceTold": ["FreeBird"],
    "TeachingOfSurvival3": ["MinstrelProblem2"],
    "GardenFun": ["FreeBird"],
    "PheromoneBomb": ["TeachingOfSurvival3"],
    "DemonstrationOfSanctuary": ["GardenFun"],
    "JoyfulJailbird": ["DemonstrationOfSanctuary"],
    "SuddenEscape": ["JoyfulJailbird"],
    "BingeParty": ["SuddenEscape"],
    "Footjob": ["BingeParty"],
    "Penance": ["Footjob"],
    "IntroductionDoe": ["Penance"],
    "CheckOfMorale2": ["IntroductionDoe"],
    "Misunderstanding": ["IntroductionDoe"],
    "Blessing": ["CheckOfMorale2"],
    "NewButler": ["Blessing"],
    "DestinyOfKleptomaniac": ["NewButler"],
    "SuddenMeeting": ["NewButler"],
    "LadyElisandra": ["DestinyOfKleptomaniac"],
    "NewAdministrator": ["LadyElisandra"],
    "TavernGossip": ["NewAdministrator"],
    "CorruptEmployee": ["TavernGossip"],
    "ReconnaissanceOfArea": ["CorruptEmployee"],
    "Rehearsal": ["ReconnaissanceOfArea"],
    "Helen": ["ReconnaissanceOfArea"],
    "ArtOfVergil5": ["NewAdministrator"],
    "MarcusAndEsther": ["ArtOfVergil5"],
}


# ============================================================
# Story definitions
# ============================================================

TIMELINES: dict[str, Timeline] = {}


def _register_story(story_name: str, story_dict: dict):

    for timeline_name, info in story_dict.items():

        TIMELINES[timeline_name] = Timeline(
            name=timeline_name,
            story=story_name,
            unlock_type=info["type"],
            unlock_value=info["value"],
            prerequisites=TIMELINE_PREREQUISITES.get(
                timeline_name,
                []
            ),
            unlock_rooms=ROOM_UNLOCKS.get(
                timeline_name,
                []
            )
        )


_register_story(
    "Demoness",
    {
        "ChibiStory":{"value":500,"type":"enslavement"},
        "RoomTour":{"value":3,"type":"days"},
        "ConspiracyWithKasra":{"value":6,"type":"days"},
        "CheckOfMorale":{"value":1250,"type":"enslavement"},
        "ArtOfVergil":{"value":1750,"type":"enslavement"},
        "ImpJokes":{"value":9,"type":"days"},
        "ArtOfVergil4":{"value":2500,"type":"enslavement"},
        "FoolsVillage":{"value":3500,"type":"enslavement"},
        "ArtOfVergil3":{"value":12,"type":"days"},
        "Tavern":{"value":6000,"type":"enslavement"},
        "ArtOfVergil2":{"value":7500,"type":"enslavement"},
        "Hamsterdig":{"value":8500,"type":"enslavement"},
        "StarrySky":{"value":15,"type":"days"},
        "MemoriesOfPose":{"value":11500,"type":"enslavement"},
        "InsideTavern":{"value":13000,"type":"enslavement"},
        "BehindTavern":{"value":14500,"type":"enslavement"},
        "PathOfDao":{"value":18,"type":"days"},
        "DepressedHero":{"value":17500,"type":"enslavement"},
        "SomethingNew3":{"value":18500,"type":"enslavement"},
        "PainfulThoughts":{"value":24,"type":"days"},
        "TownSearch":{"value":22500,"type":"enslavement"},
        "ChangesInLife":{"value":25000,"type":"enslavement"},
        "Cowgirl":{"value":27,"type":"days"},
        "СheeringUp":{"value":27500,"type":"enslavement"},
        "FreeBird":{"value":30000,"type":"enslavement"},
        "TwiceTold":{"value":33500,"type":"enslavement"},
        "GardenFun":{"value":35000,"type":"enslavement"},
        "DemonstrationOfSanctuary":{"value":37500,"type":"enslavement"},
        "SuddenEscape":{"value":40000,"type":"enslavement"},
        "IntroductionDoe":{"value":43000,"type":"enslavement"},
        "CheckOfMorale2":{"value":43000,"type":"enslavement"},
        "Blessing":{"value":50000,"type":"enslavement"},
        "ArtOfVergil5":{"value":55000,"type":"enslavement"},
    }
)

_register_story(
    "Vergil",
    {
        "SolidVergil":{"value":4500,"type":"enslavement"},
        "TableFap":{"value":500,"type":"coins"},
        "VergilSnake":{"value":750,"type":"coins"},
        "BestHero":{"value":10000,"type":"enslavement"},
        "GoblinDestroyer":{"value":0,"type":"start_boss"},
        "GoblinDestroyer2":{"value":0,"type":"win_boss"},
        "FamilyQuarrels":{"value":1600,"type":"coins"},
        "MadmanAndVergil":{"value":2000,"type":"coins"},
        "Mira":{"value":2500,"type":"coins"},
        "TeachingOfSurvival":{"value":3000,"type":"coins"},
        "Palmistry":{"value":3500,"type":"coins"},
        "SimilarityToTheHero":{"value":21,"type":"days"},
        "MadmanAndVergil2":{"value":4000,"type":"coins"},
        "EstherAndVergil":{"value":4500,"type":"coins"},
        "BaiXiAndVergil":{"value":30,"type":"days"},
        "AndroidAndVergil":{"value":4750,"type":"coins"},
        "TeachingOfSurvival2":{"value":5000,"type":"coins"},
        "EstherAndVergil2":{"value":5250,"type":"coins"},
        "MinstrelProblem":{"value":5500,"type":"coins"},
        "RobberyOfAristocrats":{"value":5750,"type":"coins"},
        "MinstrelProblem2":{"value":6000,"type":"coins"},
        "TeachingOfSurvival3":{"value":6250,"type":"coins"},
        "PheromoneBomb":{"value":6550,"type":"coins"},
    }
)

_register_story(
    "Esther",
    {
        "SomethingNew":{"value":250,"type":"coins"},
        "TestNewItem":{"value":1000,"type":"coins"},
        "SomethingNew2":{"value":1250,"type":"coins"},
        "ProblemsOfAcolytes":{"value":16000,"type":"enslavement"},
        "TestNewItem2":{"value":20000,"type":"enslavement"},
        "BloodDraw":{"value":26000,"type":"enslavement"},
        "StrangePills":{"value":31250,"type":"enslavement"},
        "ProblemsOfAcolytes2":{"value":32500,"type":"enslavement"},
        "JoyfulJailbird":{"value":33,"type":"days"},
        "NewAdministrator":{"value":52500,"type":"enslavement"},
        "MarcusAndEsther":{"value":60000,"type":"enslavement"},
    }
)


# ============================================================
# Helper API
# ============================================================

def get(name: str) -> Timeline | None:
    return TIMELINES.get(name)


def exists(name: str) -> bool:
    return name in TIMELINES


def all() -> dict[str, Timeline]:
    return TIMELINES


def names() -> list[str]:
    return sorted(TIMELINES.keys())


def by_story(story: str) -> list[Timeline]:
    return sorted(
        (
            t for t in TIMELINES.values()
            if t.story == story
        ),
        key=lambda t: t.unlock_value
    )


def prerequisites(name: str) -> list[str]:
    t = get(name)
    return t.prerequisites.copy() if t else []


def unlock_rooms(name: str) -> list[str]:
    t = get(name)
    return t.unlock_rooms.copy() if t else []