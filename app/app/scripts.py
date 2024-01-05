import json
import requests
import logging
import datetime
from django.db.models import Prefetch

from .models import *


# Setting some constants
# ----------------------


RATINGS = [0.30, 0.50, 0.70, 0.90]
SAVE_FOLDER = "saved"
LANG = "en"
BAD_SUBSTATS = ["Flat HP", "Flat ATK", "Flat DEF"]
AVERAGE_SUBSTATS = ["HP%", "DEF%", "ATK%", "Elemental Mastery", "Energy Recharge"]
GOOD_SUBSTATS = ["Crit DMG", "Crit RATE"]
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


def average(l: list) -> float:
    """Return the average of a list"""
    return sum(l) / len(l)


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
        return "good"
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


def interrogate_enka(uid: int, summary_only: bool = False) -> dict:
    """Get the informations from Enka.Network"""
    print(f"Asking Enka.Network for UID {uid}...")
    if not summary_only:
        data = requests.get(f"{BASE_URL}/{uid}").json()
        print(f"Response received")
        return data
    else:
        data = requests.get(f"{BASE_URL}/{uid}?info").json()
        print(f"Response received")
        return data



def add_player(uid: int, return_avatar: bool = False) -> None:
    """Get the informations in a human-readable format"""
    db_player = Player.objects.filter(uid=uid).first()
    if db_player is not None and db_player.updated > datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=60):
        return
    raw_data = interrogate_enka(uid)
    assert "playerInfo" in raw_data, f"No player seems to have the UID '{uid}'."
    assert "avatarInfoList" in raw_data and isinstance(raw_data["avatarInfoList"], list), f"It seems that the player with UID '{uid}' don't want to be judged."
    nickname = raw_data['playerInfo']['nickname']
    names = []
    characters_to_insert = []
    artifacts_to_insert = []
    substats_to_insert = []
    artifacts_to_drop = []
    characters_to_drop = []
    # Get avatar
    avatar = None
    if "playerInfo" not in raw_data:
        avatar = None
    if "profilePicture" not in raw_data["playerInfo"]:
        avatar = None
    if "id" in raw_data["playerInfo"]["profilePicture"]:
        avatar_id = str(raw_data["playerInfo"]["profilePicture"]["id"])
        avatar_name = PFPS[avatar_id]["iconPath"]
        avatar_name = avatar_name.replace("_Circle", "")
        avatar = f"https://enka.network/ui/{avatar_name}.png"
    elif "avatarId" in raw_data["playerInfo"]["profilePicture"]:
        # TODO: Currently not working.
        avatar_id = str(raw_data["playerInfo"]["profilePicture"]["avatarId"])
        avatar_name = LOC[LANG][str(CHARACTERS[avatar_id]["NameTextMapHash"])].split(" ")[-1]
        avatar = f"https://enka.network/ui/UI_AvatarIcon_{avatar_name}.png"
    else:
        avatar = None
    if db_player is None:
        db_player = Player.objects.create(
            uid=uid,
            nickname=nickname,
            avatar=avatar,
        )
    else:
        db_player.nickname = nickname
        db_player.avatar = avatar
        db_player.save()
    for character_index in range(len(raw_data["avatarInfoList"])):  # NOTE: usually 8
        character_obj: dict = raw_data["avatarInfoList"][character_index]
        character_name = LOC[LANG][str(CHARACTERS[str(character_obj["avatarId"])]["NameTextMapHash"])]
        character_icon = "https://enka.network/ui/{}.png".format(
            str(CHARACTERS[str(character_obj["avatarId"])]["SideIconName"]))
        print(character_icon)
        names.append(character_name)
        # characters_to_drop.append(Character.objects.filter(owner=db_player, name=character_name))
        try:
            db_character = Character(
                name=character_name,
                icon=character_icon,
                owner=db_player
            )
            characters_to_insert.append(db_character)
        except KeyError:  # Should only happen after a new character is released
            print(f"Character {character_obj['avatarId']} not found in constants/characters.json. Skipping.")
            continue
        artifacts: list = character_obj["equipList"]
        # Delete old artifacts
        # artifacts_to_drop += Artifact.objects.filter(owner=db_character)
        for artifact_index in range(len(artifacts)):  # NOTE: usually 5
            artifact_obj = artifacts[artifact_index]["flat"]
            if "equipType" not in artifact_obj:
                continue  # NOTE: weapons are stored as artifacts 
            db_artifact = Artifact(
                equiptype=EQUIPTYPE[artifact_obj["equipType"]],
                level=artifact_obj["rankLevel"] * 4,
                owner=db_character
            )
            artifacts_to_insert.append(db_artifact)
            substats_to_insert.append(
                Substat(
                    name=APPENDPROP[artifact_obj["reliquaryMainstat"]["mainPropId"]],
                    value=artifact_obj["reliquaryMainstat"]["statValue"],
                    ismainstat=True,
                    owner=db_artifact
                )
            )
            rolls = []
            for roll_id in artifacts[artifact_index]['reliquary']['appendPropIdList']:
                prop_type = [roll for roll in RELIQUARYAFFIXEXCELCONFIGDATA if roll['id'] == roll_id][0]['propType']
                prop_name = APPENDPROP[prop_type]
                rolls.append(prop_name)
            for artifact_substat_index in range(len(artifact_obj["reliquarySubstats"])):  # NOTE: usually 4
                substat_name = APPENDPROP[artifact_obj["reliquarySubstats"][artifact_substat_index]["appendPropId"]]
                substats_to_insert.append(
                    Substat(
                        name=substat_name,
                        value=artifact_obj["reliquarySubstats"][artifact_substat_index]["statValue"],
                        rolls=len([roll for roll in rolls if roll == substat_name]),
                        owner=db_artifact
                    )
                )
    
    # Artifact.objects.filter(owner__in=characters_to_insert).delete()
    Character.objects.filter(owner=db_player, name__in=names).delete()
    Character.objects.bulk_create(characters_to_insert)
    Artifact.objects.bulk_create(artifacts_to_insert)
    Substat.objects.bulk_create(substats_to_insert)


def get_substat_value(substat_name: str, artifact_substats: list) -> int:
    """Get the value of a substat from a list of substats"""
    for element in artifact_substats:
        if element.name == substat_name:
            return element.value
    return 0


def rate_artifact(artifact: Artifact, mainstat: Substat = None, substats: list[Substat] | None = None) -> dict:
    """Rates an artifact based on its substats"""
    if mainstat is None or substats is None:
        stats = Substat.objects.filter(owner=artifact)
    else:
        stats = [mainstat] + substats
    equiptype = artifact.equiptype
    # ----------------
    # Computing scores
    # ----------------
    bad_substats_count = len([substat for substat in stats if substat.name in BAD_SUBSTATS])
    average_substats_count = min(1, len([substat for substat in stats if substat.name in AVERAGE_SUBSTATS])) # Only at most 1 average substat is counted
    good_substats_count = len([substat for substat in stats if substat.name in GOOD_SUBSTATS])
    substats_score = map_range(
        x=2*good_substats_count+average_substats_count,
        x1=1,  # Min when 3 bad substats and 2 average substats
        x2=5,  # Max when 2 good substats and no bad substats (or 1 for flowers and feathers, ie. the main stat)
        y1=0,
        y2=1,
    )
    substats_score = round_to_multiple(float(substats_score), 0.1)
    # ----------------
    bad_substats_rolls = sum([
        sum([substat.rolls for substat in stats if substat.name == substat_name])
        for substat_name in BAD_SUBSTATS
    ])
    average_substats_rolls = max([
        sum([substat.rolls for substat in stats if substat.name == substat_name])
        for substat_name in AVERAGE_SUBSTATS
    ])  # Counting only the substat with the most rolls
    good_substats_rolls = sum([
        sum([substat.rolls for substat in stats if substat.name == substat_name])
        for substat_name in GOOD_SUBSTATS
    ])
    rolls_score = map_range(
        x=2*good_substats_rolls+average_substats_rolls,
        x1=1,  # Min when 8/9 rolls went to bad substats
        x2=15 if equiptype != 'Circlet' else 13,  # Max when 7/9 rolls went to good substat
        y1=0,
        y2=1,
    )
    # NOTE: Each substat has always at least one roll.
    rolls_score = round_to_multiple(float(rolls_score), 0.1)
    # ----------------
    cd = sum([substat.value for substat in stats if substat.name == 'Crit DMG'])
    cr = sum([substat.value for substat in stats if substat.name == 'Crit RATE'])
    cv = float(cd + 2 * cr)
    cv_score = map_range(
        x=cv,
        x1= 0,
        x2=50 if equiptype != 'Circlet' else 100, # For circlets, the substat can go up to 38.8% CD or ~19.4% CR, and mainstat up to 62.2% CD or 31.1% CR, which gives ~100 CV
        y1= 0,
        y2= 1,
    )
    cv_score = round_to_multiple(float(cv_score), 0.1)
    # ----------------
    score = median([substats_score, rolls_score, cv_score])
    # ----------------
    # Writing tooltips
    # ----------------
    tooltips = []
    if rating2colors(substats_score)["tttextcolor"] is not None:
        tooltips.append({
            "value": substats_score,
            "text": f"{rating2str(substats_score).capitalize()} substats",
            "textcolor": rating2colors(substats_score)["tttextcolor"],
            "textweight": rating2colors(substats_score)["tttextweight"],
        })
    if rating2colors(rolls_score)["tttextcolor"] is not None:
        tooltips.append({
            "value": rolls_score,
            "text": f"{rating2str(rolls_score).capitalize()} rolls",
            "textcolor": rating2colors(rolls_score)["tttextcolor"],
            "textweight": rating2colors(rolls_score)["tttextweight"],
        })
    if rating2colors(cv_score)["tttextcolor"] is not None:
        tooltips.append({
            "value": cv_score,
            "text": f"{rating2str(cv_score).capitalize()} crit value",
            "textcolor": rating2colors(cv_score)["tttextcolor"],
            "textweight": rating2colors(cv_score)["tttextweight"],
        })
    rating = {
        "value": score,
        "text": rating2str(score).capitalize(),
        "textcolor": rating2colors(score)["textcolor"],
        "bgcolor": rating2colors(score)["bgcolor"],
        "tooltips": tooltips,
    }
    return rating


def rate_character(scores: list) -> dict:
    """Rates a character based on the scores of its artifacts"""
    progress = 0
    progress += sum([2 if score >= RATINGS[-1] else 0 for score in scores])
    progress += sum([1 if RATINGS[-1] > score >= RATINGS[-2] else 0 for score in scores])
    progress -= sum([1 if RATINGS[0] <= score < RATINGS[1] else 0 for score in scores])
    progress -= sum([2 if score < RATINGS[0] else 0 for score in scores])
    progress = map_range(progress, -5, 5, 0, 100, True)
    progress = {
        "value": round_to_multiple(progress, 25),
        "exact": progress,
        "color": "indigo-600",
    }
    return progress


def get_avatar(uid: int) -> str:
    """Get the avatar of a player from Enka.Network"""
    print(f"Getting avatar for UID {uid}...")
    raw_data = interrogate_enka(uid)
    if "playerInfo" not in raw_data:
        return None
    if "profilePicture" not in raw_data["playerInfo"]:
        return None
    if "id" in raw_data["playerInfo"]["profilePicture"]:
        avatar_id = str(raw_data["playerInfo"]["profilePicture"]["id"])
        avatar_name = PFPS[avatar_id]["iconPath"]
        avatar_name = avatar_name.replace("_Circle", "")
        return f"https://enka.network/ui/{avatar_name}.png"
    elif "avatarId" in raw_data["playerInfo"]["profilePicture"]:
        # TODO: Currently not working.
        avatar_id = str(raw_data["playerInfo"]["profilePicture"]["avatarId"])
        avatar_name = LOC[LANG][str(CHARACTERS[avatar_id]["NameTextMapHash"])].split(" ")[-1]
        return f"https://enka.network/ui/UI_AvatarIcon_{avatar_name}.png"
    else:
        return None


def get_player(uid: int, include_rating: bool = False) -> dict:
    obj = {}
    player = Player.objects.filter(uid=uid)[0]
    obj["nickname"] = player.nickname
    obj["uid"] = player.uid
    obj["avatar"] = player.avatar
    obj["updated"] = player.updated
    obj["characters"] = []
    characters = Character.objects.filter(owner=player).select_related("owner")
    artifacts = Artifact.objects.filter(owner__in=characters).select_related("owner")
    stats = Substat.objects.filter(owner__in=artifacts).select_related("owner")
    for character in characters:
        scores = []
        obj["characters"].append({
            "name": character.name,
            "icon": character.icon,
            "artifacts": {},
        })
        characters_artifacts = [a for a in artifacts if a.owner == character]
        characters_substats = [s for s in stats if s.owner in characters_artifacts]
        # print("CHARACTER'S SUBSTATS", characters_substats)
        for equiptype in EQUIPTYPE.values():
            artifacts_ = [a for a in characters_artifacts if a.equiptype == equiptype]
            if len(artifacts_) == 0:
                obj["characters"][-1]["artifacts"][equiptype] = {
                    "mainstat": {},
                    "substats": [],
                }
                continue
            artifact = artifacts_[0]
            # print("ARTIFACT", artifact)
            artifacts_stats = [s for s in characters_substats if s.owner == artifact]
            # print("ARTIFACT'S SUBSTATS", artifacts_stats)
            equiptype = artifact.equiptype.lower()
            obj["characters"][-1]["artifacts"][equiptype] = {
                "mainstat": {},
                "substats": [],
            }
            mainstat = [stat for stat in artifacts_stats if stat.ismainstat][0]
            substats = [stat for stat in artifacts_stats if not stat.ismainstat]
            if include_rating:
                rating = rate_artifact(artifact=artifact, mainstat=mainstat, substats=substats)
                obj["characters"][-1]["artifacts"][equiptype]["rating"] = rating
                scores.append(rating["value"])
            obj["characters"][-1]["artifacts"][equiptype]["mainstat"] = {
                "name": mainstat.name,
                "value": mainstat.value,
            }
            for substat in substats:
                is_percent = "%" in substat.name or "Crit" in substat.name
                text_name = (
                    substat.name
                    .replace('Flat ', '')
                    .replace('%', '')
                    .replace('Energy Recharge', 'ER')
                    .replace('Elemental Mastery', 'EM')
                )
                textstyle = ''
                if substat.name in GOOD_SUBSTATS:
                    textstyle = 'font-bold'
                elif substat.name in AVERAGE_SUBSTATS:
                    textstyle = ''
                elif substat.name in BAD_SUBSTATS:
                    textstyle = 'italic text-opacity-50 text-black'
                obj["characters"][-1]["artifacts"][equiptype]["substats"].append({
                    "name": substat.name,
                    "value": substat.value,
                    "rolls": substat.rolls,
                    "text": f"{text_name} {substat.value}{'%' if is_percent else ''}",
                    "textstyle": textstyle
                })
        if include_rating:
            obj["characters"][-1]["progress"] = rate_character(scores)
    obj["characters"].sort(key=lambda x: x["name"])
    return obj
