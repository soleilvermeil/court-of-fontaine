import json
import requests
import logging
import datetime
import os
import glob
from .models import *


# Setting some constants
# ----------------------


RATINGS = [0.30, 0.50, 0.70, 0.90]
SAVE_FOLDER = "saved"
LANG = "en"
BAD_SUBSTATS = ["Flat HP", "Flat ATK", "Flat DEF"]
AVERAGE_SUBSTATS = ["HP%", "DEF%", "Elemental Mastery", "Energy Recharge"]
GOOD_SUBSTATS = ["ATK%", "Crit DMG", "Crit RATE"]
BASE_URL = "https://enka.network/api/uid"


# Loading some constants
# ----------------------


CHARACTERS = json.load(open('constants/characters.json'))
LOC = json.load(open('constants/loc.json', encoding="utf8"))
PFPS = json.load(open('constants/pfps.json'))
EQUIPTYPE = json.load(open('constants/EquipType.json'))
APPENDPROP = json.load(open('constants/AppendProp.json'))
RELIQUARYAFFIXEXCELCONFIGDATA = json.load(open('constants/ReliquaryAffixExcelConfigData.json'))


# General purpose functions
# -------------------------


def map_range(x, x1, x2, y1, y2, clamp: bool = False):
    """Map a value from a range to another"""
    if x1 == x2:
        return (y1 + y2) / 2
    result = (x - x1) * (y2 - y1) / (x2 - x1) + y1
    if clamp:
        result = min(max(result, y1), y2)
    return result


def median(l: list) -> float:
    """Return the median of a list"""
    if len(l) % 2 == 1:
        return sorted(l)[(len(l) - 1) // 2]
    else:
        return (sorted(l)[len(l) // 2 - 1] + sorted(l)[len(l) // 2]) / 2


def round_to_multiple(x, multiple):
    """Round a value to the nearest multiple"""
    return multiple * round(x / multiple)


# More specific functions
# -----------------------


def rating2str(rating: float) -> str:
    if rating < RATINGS[0]:
        return "terrible"
    elif rating < RATINGS[1]:
        return "bad"
    elif rating < RATINGS[2]:
        return "decent"
    elif rating < RATINGS[3]:
        return ("good")
    else:
        return "excellent"


def rating2emoji(rating: float) -> str:
    if rating < RATINGS[0]:
        return "🤢"
    elif rating < RATINGS[1]:
        return "😴"
    elif rating < RATINGS[2]:
        return "🤔"
    elif rating < RATINGS[3]:
        return "😀"
    else:
        return "😍"


def rating2colors(rating: float) -> dict:
    if rating < RATINGS[0]:
        return {
            "textcolor": "white",
            "bgcolor": "red-600",
            "tttextcolor": "red-700",
            "tttextweight": "bold",
        }
    elif rating < RATINGS[1]:
        return {
            "textcolor": "red-700",
            "bgcolor": "red-200",
            "tttextcolor": "red-700",
            "tttextweight": "normal",
        }
    elif rating < RATINGS[2]:
        return {
            "textcolor": "black",
            "bgcolor": "transparent",
            "tttextcolor": "black",
            "tttextweight": "normal",
        }
    elif rating < RATINGS[3]:
        return {
            "textcolor": "green-700",
            "bgcolor": "green-200",
            "tttextcolor": "green-700",
            "tttextweight": "normal",
        }
    else:
        return {
            "textcolor": "white",
            "bgcolor": "green-600",
            "tttextcolor": "green-700",
            "tttextweight": "bold",
        }


def interrogate_enka(uid: int) -> dict:
    """Get the informations from Enka.Network"""
    logging.debug(f"Asking Enka.Network for UID {uid}...")
    data = requests.get(f"{BASE_URL}/{uid}").json()
    logging.debug(f"Informations received!")
    return data


def add_player(uid: int, save: bool = True) -> dict:
    """Get the informations in a human-readable format"""
    raw_data = interrogate_enka(uid)
    nickname = raw_data['playerInfo']['nickname']
    db_player = Player.objects.update_or_create(
        uid=uid,
        nickname=nickname
    )[0]
    for character_index in range(len(raw_data["avatarInfoList"])):  # NOTE: usually 8
        character_obj: dict = raw_data["avatarInfoList"][character_index]
        db_character = Character.objects.update_or_create(
            name=LOC[LANG][str(CHARACTERS[str(character_obj["avatarId"])]["NameTextMapHash"])],
            owner=db_player
        )[0]
        artifacts: list = character_obj["equipList"]
        for artifact_index in range(len(artifacts)):  # NOTE: usually 5
            artifact_obj = artifacts[artifact_index]["flat"]
            if "equipType" not in artifact_obj:
                continue  # NOTE: weapons are stored as artifacts 
            db_artifact = Artifact.objects.update_or_create(
                equiptype=EQUIPTYPE[artifact_obj["equipType"]],
                # level=artifact_obj["rankLevel"] * 4,
                owner=db_character
            )[0]
            db_mainstat = Substat.objects.update_or_create(
                name=APPENDPROP[artifact_obj["reliquaryMainstat"]["mainPropId"]],
                value=artifact_obj["reliquaryMainstat"]["statValue"],
                ismainstat=True,
                owner=db_artifact
            )[0]
            rolls = []
            for roll_id in artifacts[artifact_index]['reliquary']['appendPropIdList']:
                prop_type = [roll for roll in RELIQUARYAFFIXEXCELCONFIGDATA if roll['id'] == roll_id][0]['propType']
                prop_name = APPENDPROP[prop_type]
                rolls.append(prop_name)
            for artifact_substat_index in range(len(artifact_obj["reliquarySubstats"])):  # NOTE: usually 4
                substat_name = APPENDPROP[artifact_obj["reliquarySubstats"][artifact_substat_index]["appendPropId"]]
                db_substat = Substat.objects.update_or_create(
                    name=substat_name,
                    value=artifact_obj["reliquarySubstats"][artifact_substat_index]["statValue"],
                    rolls=len([roll for roll in rolls if roll == substat_name]),
                    owner=db_artifact
                )[0]

def get_substat_value(substat_name: str, artifact_substats: list) -> int:
    """Get the value of a substat from a list of substats"""
    for element in artifact_substats:
        if element['name'] == substat_name:
            return element["value"]
    return 0


def rate_artifact(artifact: Artifact) -> float:
    substats = Substat.objects.filter(owner=artifact)
    equiptype = artifact.equiptype
    # ----------------
    # Computing scores
    # ----------------
    bad_substats_count = len(substats.filter(name__in=BAD_SUBSTATS))
    average_substats_count = len(substats.filter(name__in=AVERAGE_SUBSTATS))
    good_substats_count = len(substats.filter(name__in=GOOD_SUBSTATS))
    substats_score = map_range(
        x=good_substats_count + min(1, average_substats_count) - bad_substats_count,
        x1=0,
        x2=4 if equiptype != 'Circlet' else 3,
        y1=0,
        y2=1,
    )
    # ----------------
    bad_substats_rolls = sum([0] + [
        substats.filter(name=substat_name).first().rolls for substat_name in BAD_SUBSTATS
        if substats.filter(name=substat_name).exists()
    ])
    average_substats_rolls = max([0] + [
        substats.filter(name=substat_name).first().rolls for substat_name in AVERAGE_SUBSTATS
        if substats.filter(name=substat_name).exists()
    ])
    good_substats_rolls = sum([0] + [
        substats.filter(name=substat_name).first().rolls for substat_name in GOOD_SUBSTATS
        if substats.filter(name=substat_name).exists()
    ])
    rolls_score = map_range(
        x=good_substats_rolls + average_substats_rolls - bad_substats_rolls,
        x1=0,
        x2=8,
        y1=0,
        y2=1,
    )
    # ----------------
    cd = substats.filter(name="Crit DMG").first().value if substats.filter(name="Crit DMG").exists() else 0
    cr = substats.filter(name="Crit RATE").first().value if substats.filter(name="Crit RATE").exists() else 0
    cv = cd + 2 * cr
    cv_score = map_range(cv, 0, 50 if equiptype != 'Circlet' else 25, 0, 1)
    # ----------------
    # score = 1 / 3 * (substats_score + rolls_score + cv_score)
    score = median([substats_score, rolls_score, cv_score])
    # score = 0
    # score += sum([2 if s >= RATINGS[-1] else 0 for s in [substats_score, rolls_score, cv_score]])
    # score += sum([1 if RATINGS[-1] > s >= RATINGS[-2] else 0 for s in [substats_score, rolls_score, cv_score]])
    # score -= sum([1 if RATINGS[0] <= s < RATINGS[1] else 0 for s in [substats_score, rolls_score, cv_score]])
    # score -= sum([2 if s < RATINGS[0] else 0 for s in [substats_score, rolls_score, cv_score]])
    # score = map_range(score, -6, 6, 0, 1, True)

    # ----------------
    # Writing tooltips
    # ----------------
    tooltips = []
    if rating2colors(substats_score)["tttextcolor"] is not None:
        tooltips.append({
            "text": f"{rating2str(substats_score).capitalize()} substats",
            "textcolor": rating2colors(substats_score)["tttextcolor"],
            "textweight": rating2colors(substats_score)["tttextweight"],
        })
    if rating2colors(rolls_score)["tttextcolor"] is not None:
        tooltips.append({
            "text": f"{rating2str(rolls_score).capitalize()} rolls",
            "textcolor": rating2colors(rolls_score)["tttextcolor"],
            "textweight": rating2colors(rolls_score)["tttextweight"],
        })
    if rating2colors(cv_score)["tttextcolor"] is not None:
        tooltips.append({
            "text": f"{rating2str(cv_score).capitalize()} crit value",
            "textcolor": rating2colors(cv_score)["tttextcolor"],
            "textweight": rating2colors(cv_score)["tttextweight"],
        })
    rating = {
        "text": rating2str(score).capitalize(),
        "textcolor": rating2colors(score)["textcolor"],
        "bgcolor": rating2colors(score)["bgcolor"],
        "tooltips": tooltips,
    }
    return rating

def get_player(uid: int, include_rating: bool = False) -> dict:
    obj = {}
    player = Player.objects.filter(uid=uid)[0]
    obj["nickname"] = player.nickname
    obj["uid"] = player.uid
    obj["characters"] = []
    characters = Character.objects.filter(owner=player)
    for character in characters:
        obj["characters"].append({
            "name": character.name,
            "artifacts": {},
        })
        artifacts = Artifact.objects.filter(owner=character)
        for artifact in artifacts:
            equiptype = artifact.equiptype.lower()
            obj["characters"][-1]["artifacts"][equiptype] = {
                "mainstat": {},
                "substats": [],
            }
            if include_rating:
                obj["characters"][-1]["artifacts"][equiptype]["rating"] = rate_artifact(artifact)
            mainstat = Substat.objects.filter(owner=artifact, ismainstat=True)[0]
            obj["characters"][-1]["artifacts"][equiptype]["mainstat"] = {
                "name": mainstat.name,
                "value": mainstat.value,
            }
            substats = Substat.objects.filter(owner=artifact, ismainstat=False)
            for substat in substats:
                obj["characters"][-1]["artifacts"][equiptype]["substats"].append({
                    "name": substat.name,
                    "value": substat.value,
                    "rolls": substat.rolls,
                })
    return obj