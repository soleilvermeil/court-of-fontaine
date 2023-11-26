import json
import requests
import logging
import datetime
import os
import math


RATINGS = [0.30, 0.50, 0.70, 0.90]
SAVE_FOLDER = "saved"
LANG = "en"
BAD_SUBSTATS = ["Flat HP", "Flat ATK", "Flat DEF"]
AVERAGE_SUBSTATS = ["HP%", "DEF%", "Elemental Mastery", "Energy Recharge"]
GOOD_SUBSTATS = ["ATK%", "Crit DMG", "Crit RATE"]
BASE_URL = "https://enka.network/api/uid"
CHARACTERS = json.load(open('constants/characters.json'))
LOC = json.load(open('constants/loc.json', encoding="utf8"))
PFPS = json.load(open('constants/pfps.json'))
EQUIPTYPE = json.load(open('constants/EquipType.json'))
APPENDPROP = json.load(open('constants/AppendProp.json'))
RELIQUARYAFFIXEXCELCONFIGDATA = json.load(open('constants/ReliquaryAffixExcelConfigData.json'))


def map_range(x, x1, x2, y1, y2, clamp: bool = False):
    """Map a value from a range to another"""
    if x1 == x2:
        return (y1 + y2) / 2
    result = (x - x1) * (y2 - y1) / (x2 - x1) + y1
    if clamp:
        result = min(max(result, y1), y2)
    return result


def round_to_multiple(x, multiple):
    """Round a value to the nearest multiple"""
    return multiple * round(x / multiple)


def get_infos(uid: int) -> dict:
    """Get the informations from Enka.Network"""
    logging.debug(f"Asking Enka.Network for UID {uid}...")
    data = requests.get(f"{BASE_URL}/{uid}").json()
    logging.debug(f"Informations received!")
    return data


def get_avatar(data: dict) -> str:
    """Get the avatar of a player from Enka.Network"""
    if "id" in data["playerInfo"]["profilePicture"]:
        avatar_id = str(data["playerInfo"]["profilePicture"]["id"])
        avatar_name = PFPS[avatar_id]["iconPath"]
        avatar_name = avatar_name.replace("_Circle", "")
        return f"https://enka.network/ui/{avatar_name}.png"
    elif "avatarId" in data["playerInfo"]["profilePicture"]:
        # TODO: Currently not working.
        avatar_id = str(data["playerInfo"]["profilePicture"]["avatarId"])
        avatar_name = LOC[LANG][str(CHARACTERS[avatar_id]["NameTextMapHash"])].split(" ")[-1]
        return f"https://enka.network/ui/UI_AvatarIcon_{avatar_name}.png"
    else:
        return ""


def get_substat_value(substat_name: str, artifact_substats: list) -> int:
    """Get the value of a substat from a list of substats"""
    for element in artifact_substats:
        if element['name'] == substat_name:
            return element["value"]
    return 0  


def reformat_infos(old_data: dict) -> dict:
    """Reformat the data from Enka.Network to a more usable format"""
    better_data = {
        "uid": old_data['uid'],
        "datetime": datetime.datetime.now().isoformat(),
        "characters": [],
    }
    for character_index in range(len(old_data["avatarInfoList"])):  # NOTE: usually 8
        character_obj: dict = old_data["avatarInfoList"][character_index]
        character_name: str = LOC[LANG][str(CHARACTERS[str(character_obj["avatarId"])]["NameTextMapHash"])]
        better_data["characters"].append({
            "name": character_name,
            "artifacts": {
                equiptype.lower(): {
                    "level": 0,
                    "mainstat": {},
                    "substats": [],
                } for equiptype in EQUIPTYPE.values()
            }
        })
        artifacts: list = character_obj["equipList"]
        for artifact_index in range(len(artifacts)):  # NOTE: usually 5
            artifact_obj = artifacts[artifact_index]["flat"]
            if "equipType" not in artifact_obj:
                continue  # NOTE: weapons are stored as artifacts
            artifact_type = EQUIPTYPE[artifact_obj["equipType"]]
            artifact_level = artifact_obj["rankLevel"] * 4
            artifact_mainstat = (
                APPENDPROP[artifact_obj["reliquaryMainstat"]["mainPropId"]],
                artifact_obj["reliquaryMainstat"]["statValue"]
            )
            better_data["characters"][character_index]["artifacts"][artifact_type.lower()]["level"] = artifact_level
            better_data["characters"][character_index]["artifacts"][artifact_type.lower()]["mainstat"] = {
                "name": artifact_mainstat[0],
                "value": artifact_mainstat[1]
            }
            rolls = []
            for roll_id in artifacts[artifact_index]['reliquary']['appendPropIdList']:
                prop_type = [roll for roll in RELIQUARYAFFIXEXCELCONFIGDATA if roll['id'] == roll_id][0]['propType']
                prop_name = APPENDPROP[prop_type]
                rolls.append(prop_name)
            for artifact_substat_index in range(len(artifact_obj["reliquarySubstats"])):  # NOTE: usually 4
                artifact_substat = (
                    APPENDPROP[artifact_obj["reliquarySubstats"][artifact_substat_index]["appendPropId"]],
                    artifact_obj["reliquarySubstats"][artifact_substat_index]["statValue"]
                )
                better_data["characters"][character_index]["artifacts"][artifact_type.lower()]["substats"].append({
                    "name": artifact_substat[0],
                    "value": artifact_substat[1],
                    'rolls': len([roll for roll in rolls if roll == artifact_substat[0]]),
                })
    return better_data


def combine_infos(data: dict) -> dict:
    """Combine the (reformatted) data from Enka.Network and the saved data"""
    uid = data["uid"]
    filename = os.path.join(SAVE_FOLDER, f'data_{uid}.json')
    if not os.path.exists(filename):
        return sort_infos(data)
    else:
        saved_data = json.load(open(filename))
        for saved_character in saved_data["characters"]:
            if not any([saved_character["name"] == character["name"] for character in data["characters"]]):
                data["characters"].append(saved_character)
        return sort_infos(data)


def rating2str(rating: float) -> str:
    if rating < RATINGS[0]:
        return "terrible"
    elif rating < RATINGS[1]:
        return "bad"
    elif rating < RATINGS[2]:
        return "decent"
    elif rating < RATINGS[3]:
        return "very good"
    else:
        return "jewel"


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


def rate(data: dict) -> dict:
    """Rate the artifacts of a player"""
    rating = {"characters": []}
    for character in data["characters"]:
        rating["characters"].append({
            "name": character["name"],
            "progress": {
                "value": 0,
                "color": "",
            },
            "artifacts": {}
        })
        scores = [0] * len(EQUIPTYPE)
        for artifact_type in EQUIPTYPE.values():
            artifact_obj = character["artifacts"][artifact_type.lower()]
            artifact_substats = artifact_obj["substats"]
            # ----------------
            # Computing scores
            # ----------------
            bad_substats_count = len([
                bad_substat for bad_substat in BAD_SUBSTATS
                if get_substat_value(substat_name=bad_substat, artifact_substats=artifact_substats) > 0
            ])
            average_substats_count = len([
                average_substat for average_substat in AVERAGE_SUBSTATS
                if get_substat_value(substat_name=average_substat, artifact_substats=artifact_substats) > 0
            ])
            good_substats_count = len([
                good_substat for good_substat in GOOD_SUBSTATS
                if get_substat_value(substat_name=good_substat, artifact_substats=artifact_substats) > 0
            ])
            substats_score = map_range(
                x=good_substats_count + min(1, average_substats_count) - bad_substats_count,
                x1=0,
                x2=4 if artifact_type != 'Circlet' else 3,
                y1=0,
                y2=1,
            )
            # ----------------
            bad_substats_rolls = sum([0] + [
                artifact_substat['rolls'] for artifact_substat in artifact_substats
                if artifact_substat['name'] in BAD_SUBSTATS
            ])
            average_substats_rolls = max([0] + [
                artifact_substat['rolls'] for artifact_substat in artifact_substats
                if artifact_substat['name'] in AVERAGE_SUBSTATS
            ])
            good_substats_rolls = sum([0] + [
                artifact_substat['rolls'] for artifact_substat in artifact_substats
                if artifact_substat['name'] in GOOD_SUBSTATS
            ])
            rolls_score = map_range(
                x=good_substats_rolls + average_substats_rolls - bad_substats_rolls,
                x1=0,
                x2=8,
                y1=0,
                y2=1,
            )
            # ----------------
            cd = get_substat_value(substat_name="Crit DMG", artifact_substats=artifact_substats)
            cr = get_substat_value(substat_name="Crit RATE", artifact_substats=artifact_substats)
            cv = cd + 2 * cr
            cv_score = map_range(cv, 0, 50 if artifact_type != 'Circlet' else 25, 0, 1)
            # ----------------
            # score = 1 / 3 * (substats_score + rolls_score + cv_score)
            score = sorted([substats_score, rolls_score, cv_score])[1]
            # score = 0
            # score += sum([2 if s >= RATINGS[-1] else 0 for s in [substats_score, rolls_score, cv_score]])
            # score += sum([1 if RATINGS[-1] > s >= RATINGS[-2] else 0 for s in [substats_score, rolls_score, cv_score]])
            # score -= sum([1 if RATINGS[0] <= s < RATINGS[1] else 0 for s in [substats_score, rolls_score, cv_score]])
            # score -= sum([2 if s < RATINGS[0] else 0 for s in [substats_score, rolls_score, cv_score]])
            # score = map_range(score, -6, 6, 0, 1, True)
            scores[list(EQUIPTYPE.values()).index(artifact_type)] = score
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
            rating["characters"][-1]["artifacts"][artifact_type.lower()] = {
                "rating": {
                    "text": rating2str(score).capitalize(),
                    "textcolor": rating2colors(score)["textcolor"],
                    "bgcolor": rating2colors(score)["bgcolor"],
                },
                "tooltips": tooltips,
            }
        # ------------------
        # Computing progress
        # ------------------
        progress = 0
        progress += sum([2 if score >= RATINGS[-1] else 0 for score in scores])
        progress += sum([1 if RATINGS[-1] > score >= RATINGS[-2] else 0 for score in scores])
        progress -= sum([1 if RATINGS[0] <= score < RATINGS[1] else 0 for score in scores])
        progress -= sum([2 if score < RATINGS[0] else 0 for score in scores])
        progress = map_range(progress, -5, 5, 0, 100, True)
        rating["characters"][-1]["progress"]["value"] = round_to_multiple(progress, 25)
        rating["characters"][-1]["progress"]["color"] = "indigo-600"
    return rating

def sort_infos(rating: dict) -> dict:
    """Sort infos alphabetically"""
    rating["characters"] = sorted(rating["characters"], key=lambda x: x["name"])
    return rating


def save(data: dict) -> None:
    """Save the passed data to a file"""
    uid = data["uid"]    
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    filename = os.path.join(SAVE_FOLDER, f'data_{uid}.json')
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
