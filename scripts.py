import json
import requests
import logging
import argparse
import datetime
import os
import shutil


LINE_WIDTH = 40

def map_range(x, x1, x2, y1, y2, clamp=False):
    result = (x - x1) * (y2 - y1) / (x2 - x1) + y1
    if clamp:
        result = min(max(result, y1), y2)
    return result

def round_to_multiple(x, multiple):
    return multiple * round(x / multiple)

def get_infos(uid: int) -> dict:
    """Get the informations from Enka.Network"""
    logging.debug(f"Asking Enka.Network for UID {uid}...")
    BASE_URL = "https://enka.network/api/uid"
    data = requests.get(f"{BASE_URL}/{uid}").json()
    logging.debug(f"Informations received!")
    return data

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
    CHARACTERS = json.load(open('constants/characters.json'))
    LOC = json.load(open('constants/loc.json', encoding="utf8"))
    LANG = "en"
    EQUIPTYPE = json.load(open('constants/EquipType.json'))
    APPENDPROP = json.load(open('constants/AppendProp.json'))
    RELIQUARYAFFIXEXCELCONFIGDATA = json.load(open('constants/ReliquaryAffixExcelConfigData.json'))
    for character_index in range(len(old_data["avatarInfoList"])): # NOTE: usually 8
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
        for artifact_index in range(len(artifacts)): # NOTE: usually 5
            artifact_obj = artifacts[artifact_index]["flat"]
            if not "equipType" in artifact_obj: continue # NOTE: weapons are stored as artifacts
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
            for artifact_substat_index in range(len(artifact_obj["reliquarySubstats"])): # NOTE: usually 4
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

RATINGS = [0.30, 0.50, 0.70, 0.90]

def rating2str(rating: float) -> str:
    if rating < RATINGS[0]: return "terrible"
    elif rating < RATINGS[1]: return "bad"
    elif rating < RATINGS[2]: return "decent"
    elif rating < RATINGS[3]: return "very good"
    else: return "jewel"

def rating2emoji(rating: float) -> str:
    if rating < RATINGS[0]: return "🤢"
    elif rating < RATINGS[1]: return "😴"
    elif rating < RATINGS[2]: return "🤔"
    elif rating < RATINGS[3]: return "😀"
    else: return "😍"

def rating2colors(rating: float) -> dict:
    if rating < RATINGS[0]: return {"textcolor": "white", "bgcolor": "red-600", "tttextcolor": "red-700", "tttextweight": "bold"}
    elif rating < RATINGS[1]: return {"textcolor": "red-700", "bgcolor": "red-200", "tttextcolor": "red-700", "tttextweight": "normal"}
    elif rating < RATINGS[2]: return {"textcolor": "black", "bgcolor": "transparent", "tttextcolor": "black", "tttextweight": "normal"}
    elif rating < RATINGS[3]: return {"textcolor": "green-700", "bgcolor": "green-200", "tttextcolor": "green-700", "tttextweight": "normal"}
    else: return {"textcolor": "white", "bgcolor": "green-600", "tttextcolor": "green-700", "tttextweight": "bold"}

def rate(data: dict) -> dict:
    """Rate the artifacts of a player"""
    rating = {"characters": []}
    EQUIPTYPE: dict = json.load(open('constants/EquipType.json'))
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
            BAD_SUBSTATS = ["Flat HP", "Flat ATK", "Flat DEF"]
            AVERAGE_SUBSTATS = ["HP%", "DEF%", "Elemental Mastery", "Energy Recharge"]
            GOOD_SUBSTATS = ["ATK%", "Crit DMG", "Crit RATE"]
            artifact_obj = character["artifacts"][artifact_type.lower()]
            artifact_substats = artifact_obj["substats"]
            # ----------------
            # Computing scores
            # ----------------
            bad_substats_count = len([bad_substat for bad_substat in BAD_SUBSTATS if get_substat_value(substat_name=bad_substat, artifact_substats=artifact_substats) > 0])
            average_substats_count = len([average_substat for average_substat in AVERAGE_SUBSTATS if get_substat_value(substat_name=average_substat, artifact_substats=artifact_substats) > 0])
            good_substats_count = len([good_substat for good_substat in GOOD_SUBSTATS if get_substat_value(substat_name=good_substat, artifact_substats=artifact_substats) > 0])
            substats_score = map_range(good_substats_count + min(1, average_substats_count) - bad_substats_count, 0, 4 if artifact_type != 'Circlet' else 3, 0, 1)
            bad_substats_rolls = sum([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in BAD_SUBSTATS])
            average_substats_rolls = max([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in AVERAGE_SUBSTATS])
            good_substats_rolls = sum([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in GOOD_SUBSTATS])
            rolls_score = map_range(good_substats_rolls + average_substats_rolls - bad_substats_rolls, 0, 8, 0, 1)
            cd = get_substat_value(substat_name="Crit DMG", artifact_substats=artifact_substats)
            cr = get_substat_value(substat_name="Crit RATE", artifact_substats=artifact_substats)
            cv = cd + 2 * cr
            cv_score = map_range(cv, 0, 50 if artifact_type != 'Circlet' else 25, 0, 1)
            score = 1 / 3 * (substats_score + rolls_score + cv_score)
            scores[list(EQUIPTYPE.values()).index(artifact_type)] = score
            # ----------------
            tooltips = []
            if rating2colors(rolls_score)["tttextcolor"] is not None:
                tooltips.append({
                    "text": f"{rating2str(rolls_score).capitalize()} rolls",
                    "textcolor": rating2colors(rolls_score)["tttextcolor"],
                    "textweight": rating2colors(rolls_score)["tttextweight"],
                })
            if rating2colors(substats_score)["tttextcolor"] is not None:
                tooltips.append({
                    "text": f"{rating2str(substats_score).capitalize()} substats",
                    "textcolor": rating2colors(substats_score)["tttextcolor"],
                    "textweight": rating2colors(substats_score)["tttextweight"],
                })
            if rating2colors(cv_score)["tttextcolor"] is not None:
                tooltips.append({
                    "text": f"{rating2str(cv_score).capitalize()} crit value",
                    "textcolor": rating2colors(cv_score)["tttextcolor"],
                    "textweight": rating2colors(cv_score)["tttextweight"],
                })
            # ----------------
            rating["characters"][-1]["artifacts"][artifact_type.lower()] = {
                "rating": {
                    "text": rating2str(score).capitalize(),
                    "textcolor": rating2colors(score)["textcolor"],
                    "bgcolor": rating2colors(score)["bgcolor"],
                },
                "tooltips": tooltips,
            }
        progress = 0
        progress += sum([2 if score >= RATINGS[-1] else 0 for score in scores])
        progress += sum([1 if RATINGS[-1] > score >= RATINGS[-2] else 0 for score in scores])
        progress -= sum([1 if RATINGS[0] <= score < RATINGS[1] else 0 for score in scores])
        progress -= sum([2 if score < RATINGS[0] else 0 for score in scores])
        progress = map_range(progress, -5, 5, 0, 100, True)
        rating["characters"][-1]["progress"]["value"] = round_to_multiple(progress, 10)
        rating["characters"][-1]["progress"]["color"] = "indigo-600"
    return rating

def print_rating(data: dict, character_index: int) -> None:
    """Print the rating of a character in a human-readable format"""
    EQUIPTYPE: dict = json.load(open('constants/EquipType.json'))
    character_name = data["characters"][character_index]["name"]
    print("=" * LINE_WIDTH)
    print(f"{character_name}")
    print("=" * LINE_WIDTH)
    scores = []
    for artifact_type in EQUIPTYPE.values():
        if artifact_type.lower() == "circlet": continue
        artifact_obj = data["characters"][character_index]["artifacts"][artifact_type.lower()]
        print(artifact_type)
        artifact_substats = artifact_obj["substats"]
        BAD_SUBSTATS = ["Flat HP", "Flat ATK", "Flat DEF"]
        AVERAGE_SUBSTATS = ["HP%", "DEF%", "Elemental Mastery", "Energy Recharge"]
        GOOD_SUBSTATS = ["ATK%", "Crit DMG", "Crit RATE"]
        # ----------------
        # Computing scores
        # ----------------
        bad_substats_count = len([bad_substat for bad_substat in BAD_SUBSTATS if get_substat_value(substat_name=bad_substat, artifact_substats=artifact_substats) > 0])
        average_substats_count = len([average_substat for average_substat in AVERAGE_SUBSTATS if get_substat_value(substat_name=average_substat, artifact_substats=artifact_substats) > 0])
        good_substats_count = len([good_substat for good_substat in GOOD_SUBSTATS if get_substat_value(substat_name=good_substat, artifact_substats=artifact_substats) > 0])
        substats_score = good_substats_count + min(1, average_substats_count) - bad_substats_count
        print(f" - {bad_substats_count} bad substats")
        print(f" - {average_substats_count} average substats")
        print(f" - {good_substats_count} good substats")
        # ----------------
        bad_substats_rolls = sum([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in BAD_SUBSTATS])
        average_substats_rolls = max([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in AVERAGE_SUBSTATS])
        good_substats_rolls = sum([0] + [artifact_substat['rolls'] for artifact_substat in artifact_substats if artifact_substat['name'] in GOOD_SUBSTATS])
        rolls_score = good_substats_rolls + average_substats_rolls - bad_substats_rolls
        print(f"=> {rating2emoji(map_range(substats_score, 0, 4, 0, 1))} {rating2str(map_range(substats_score, 0, 4, 0, 1)).upper()}")
        print(f" - {bad_substats_rolls} bad substats rolls")
        print(f" - {average_substats_rolls} average (effective) substats rolls")
        print(f" - {good_substats_rolls} good substats rolls")
        print(f"=> {rating2emoji(map_range(rolls_score, 0, 9, 0, 1))} {rating2str(map_range(rolls_score, 0, 9, 0, 1)).upper()}")
        # ----------------
        cd = get_substat_value(substat_name="Crit DMG", artifact_substats=artifact_substats)
        cr = get_substat_value(substat_name="Crit RATE", artifact_substats=artifact_substats)
        cv = cd + 2 * cr
        print(f" - {cd:0>4.1f}% of Crit DMG")
        print(f" - {cr:0>4.1f}% of Crit RATE")
        print(f" - {cv:0>4.1f}% of Crit VALUE")
        print(f"=> {rating2emoji(map_range(cv, 0, 50, 0, 1))} {rating2str(map_range(cv, 0, 50, 0, 1)).upper()}")
        # ----------------
        score = 1/2 * (map_range(cv, 0, 50, 0, 1) + map_range(rolls_score, 0, 9, 0, 1))
        print(f"Overall {rating2emoji(score)} {rating2str(score).upper()}")
        scores.append(score)
        print(f"-" * LINE_WIDTH)
    print(f"Overall {rating2emoji(sum(scores) / len(scores))} {rating2str(sum(scores) / len(scores)).upper():<9}")
    

if __name__ == "__main__":

    # Setting up logging
    # ------------------

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%y-%m-%d %H:%M:%S"
    )

    # Setting up arguments
    # --------------------

    parser = argparse.ArgumentParser(description="Enka.Network CLI")
    parser.add_argument("--uid", type=int, help="UID of the player", required=True)
    parser.add_argument("--save", help="Save the data to a file", action="store_true")
    parser.add_argument('--reset', help='Reset the data', action='store_true')
    uid = parser.parse_args().uid
    save = parser.parse_args().save
    reset = parser.parse_args().reset

    # Getting infos
    # -------------

    infos = get_infos(uid)
    data = reformat_infos(infos)

    # Rating
    # ------

    for character_index in range(len(data["characters"])):
        print_rating(data=data, character_index=character_index)
    rating = rate(data=data)

    # Resetting
    # ---------

    if reset:
        try:
            shutil.rmtree(os.path.join('data', str(uid)))
        except FileNotFoundError:
            pass

    # Saving
    # ------

    if save:
        if not os.path.exists(os.path.join('data', str(uid))):
            os.makedirs(os.path.join('data', str(uid)))
        identifier = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        with open(os.path.join('data', str(uid), f'data_{identifier}.json'), "w") as f:
            json.dump(data, f, indent=4)
        with open(os.path.join('data', str(uid),f'rating_{identifier}.json' ), "w") as f:
            json.dump(rating, f, indent=4)