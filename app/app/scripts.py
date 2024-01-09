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


def centile(l: list, p: float) -> float:
    """Return the pth centile of a list"""
    # Ensure the input list is not empty
    if not l:
        raise ValueError("Input list cannot be empty")

    # Sort the list in ascending order
    sorted_l = sorted(l)

    # Calculate the index using linear interpolation
    index = p * (len(sorted_l) - 1)

    # Find the values at the floor and ceiling indices
    floor_index = int(index)
    ceil_index = floor_index + 1

    # If the index is a whole number, return the corresponding value
    if index.is_integer():
        return sorted_l[int(index)]

    # Linear interpolation
    floor_value = float(sorted_l[floor_index])
    ceil_value = float(sorted_l[ceil_index])
    interpolated_value = (1 - (index % 1)) * floor_value + (index % 1) * ceil_value

    return interpolated_value


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
        response = requests.get(f"{BASE_URL}/{uid}")
        if response.status_code != 200:
            print(f"Response code {response.status_code}.")
            return response.json()
        data = response.json()
        print(f"Response received!")
        return data
    else:
        response = requests.get(f"{BASE_URL}/{uid}?info")
        if response.status_code != 200:
            print(f"Response code {response.status_code}.")
            return response.json()
        data = response.json()
        print(f"Response received!")
        return data


def get_character_hp(fightPropMap: dict) -> float:
    """Get the HP of a character from its fightPropMap"""
    base_hp = fightPropMap["1"]
    hp_flat = 0 if "2" not in fightPropMap else fightPropMap["2"]
    hp_percent = 0 if "3" not in fightPropMap else fightPropMap["3"]
    return base_hp * (1 + hp_percent) + hp_flat


def get_character_atk(fightPropMap: dict) -> float:
    """Get the ATK of a character from its fightPropMap"""
    base_atk = fightPropMap["4"]
    atk_flat = 0 if "5" not in fightPropMap else fightPropMap["5"]
    atk_percent = 0 if "6" not in fightPropMap else fightPropMap["6"]
    return base_atk * (1 + atk_percent) + atk_flat


def get_character_def(fightPropMap: dict) -> float:
    """Get the DEF of a character from its fightPropMap"""
    base_def = fightPropMap["7"]
    def_flat = 0 if "8" not in fightPropMap else fightPropMap["8"]
    def_percent = 0 if "9" not in fightPropMap else fightPropMap["9"]
    return base_def * (1 + def_percent) + def_flat


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
        if avatar_id == "10000052":
            avatar_id = "3900"
            avatar_name = PFPS[avatar_id]["iconPath"]
            avatar_name = avatar_name.replace("_Circle", "")
            avatar = f"https://enka.network/ui/{avatar_name}.png"
        else:
            avatar_name = LOC[LANG][str(CHARACTERS[avatar_id]["NameTextMapHash"])].split(" ")
            avatar = f"https://enka.network/ui/UI_AvatarIcon_{avatar_name[0]}.png"
            request = requests.get(avatar)
            if request.status_code != 200:
                avatar = f"https://enka.network/ui/UI_AvatarIcon_{avatar_name[-1]}.png"
    else:
        avatar = None
    print(type(uid))
    if uid == "703047530":
        avatar = "/static/eastereggs/soleil.png"
    elif uid == "606062036":
        avatar = "/static/eastereggs/eiko.png"
    if db_player is None:
        db_player = Player.objects.create(
            uid=uid,
            nickname=nickname,
            avatar=avatar
        )
    else:
        db_player.nickname = nickname
        db_player.avatar = avatar
        db_player.save()
    for character_index in range(len(raw_data["avatarInfoList"])):  # NOTE: usually 8
        character_obj: dict = raw_data["avatarInfoList"][character_index]
        character_name = LOC[LANG][str(CHARACTERS[str(character_obj["avatarId"])]["NameTextMapHash"])]
        names.append(character_name)
        character_icon = "https://enka.network/ui/UI_AvatarIcon_{}.png".format(
            str(CHARACTERS[str(character_obj["avatarId"])]["SideIconName"]).split("_")[-1])
        try:
            db_character = Character(
                name=character_name,
                icon=character_icon,
                stat_hp=get_character_hp(character_obj["fightPropMap"]),
                stat_atk=get_character_atk(character_obj["fightPropMap"]),
                stat_def=get_character_def(character_obj["fightPropMap"]),
                stat_cr=character_obj["fightPropMap"]["20"] * 100,
                stat_cd=character_obj["fightPropMap"]["22"] * 100,
                stat_er=character_obj["fightPropMap"]["23"] * 100,
                stat_em=character_obj["fightPropMap"]["28"],
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
            if "appendPropIdList" not in artifacts[artifact_index]['reliquary']:
                continue # NOTE: This happens when a low quality artifact has no substats.
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
    if len(scores) == 0:
        progress = -2 * 5
    truevalue = map_range(progress, -5, 5, 0, 100, clamp=False)
    progress = map_range(progress, -5, 5, 0, 100, clamp=True)
    progress = {
        "value": round_to_multiple(progress, 25),
        "truevalue": int(truevalue),
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
    player = Player.objects.get(uid=uid)
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
            "stat_hp": character.stat_hp,
            "stat_atk": character.stat_atk,
            "stat_def": character.stat_def,
            "stat_cr": character.stat_cr,
            "stat_cd": character.stat_cd,
            "stat_er": character.stat_er,
            "stat_em": character.stat_em,
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
            rating = rate_artifact(artifact=artifact, mainstat=mainstat, substats=substats)
            obj["characters"][-1]["artifacts"][equiptype]["rating"] = rating
            scores.append(rating["value"])
            # obj["characters"][-1]["artifacts"][equiptype]["mainstat"] = {
            #     "name": mainstat.name,
            #     "value": mainstat.value,
            # }
            for i, stat in enumerate([mainstat] + substats):
                is_percent = "%" in stat.name or "Crit" in stat.name or "Bonus" in stat.name
                text_name = (
                    stat.name
                    .replace('Flat ', '')
                    .replace('%', '')
                    .replace('Energy Recharge', 'ER')
                    .replace('Elemental Mastery', 'EM')
                    .replace('Crit DMG', 'CD')
                    .replace('Crit RATE', 'CR')
                    .replace(' DMG Bonus', '')
                )
                textstyle = ''
                if stat.name in GOOD_SUBSTATS:
                    textstyle = 'font-bold'
                elif stat.name in AVERAGE_SUBSTATS:
                    textstyle = ''
                elif stat.name in BAD_SUBSTATS:
                    textstyle = 'italic text-opacity-30 text-black'
                text = f"{text_name}+{stat.value:.{0 if 'Flat' in stat.name else 1}f}{'%' if is_percent else ''}"
                if i == 0: # Main stat
                    obj["characters"][-1]["artifacts"][equiptype]["mainstat"] = {
                        "name": stat.name,
                        "value": stat.value,
                        "text": text,
                        "textstyle": textstyle,
                    }
                else:
                    obj["characters"][-1]["artifacts"][equiptype]["substats"].append({
                        "name": stat.name,
                        "value": stat.value,
                        "rolls": stat.rolls,
                        "text": text,
                        "textstyle": textstyle,
                    })
            for _ in range(4 - len(substats)):
                obj["characters"][-1]["artifacts"][equiptype]["substats"].append({
                    "name": None,
                    "value": None,
                    "rolls": 0,
                    "text": "-",
                    "textstyle": 'italic text-opacity-0 text-black',
                })
        obj["characters"][-1]["progress"] = rate_character(scores)
    # obj["characters"].sort(key=lambda x: x["name"])
    obj["characters"].sort(key=lambda x: x["progress"]["truevalue"], reverse=True)
    return obj


def get_characters(name: str) -> list:
    print(f"Getting characters for name {name}...")
    characters = Character.objects.filter(name__iexact=name.replace("_", " ")).select_related("owner")
    characters = [c for c in characters]
    assert len(characters) > 0, f"It seems that no players have '{name}' in their showcase."
    print(characters)
    obj = {
        "name": characters[0].name,
        "icon": characters[0].icon,
        "characters": [],
    }
    values_hp = [character.stat_hp for character in characters]
    values_atk = [character.stat_atk for character in characters]
    values_def = [character.stat_def for character in characters]
    values_cr = [character.stat_cr for character in characters]
    values_cd = [character.stat_cd for character in characters]
    values_er = [character.stat_er for character in characters]
    values_em = [character.stat_em for character in characters]
    def get_style(value: float, values: list) -> str:
        if value < centile(values, 0.25):
            return "italic text-opacity-30 text-black"
        elif value > centile(values, 0.75):
            return "font-bold"
        else:
            return ""

    for character in characters:
        obj["characters"].append({
            "owner": {
                "name": character.owner.nickname,
                "uid": character.owner.uid,
                "avatar": character.owner.avatar,
            },
            "stat_hp": {
                "value": character.stat_hp,
                "style": get_style(character.stat_hp, values_hp),
            },
            "stat_atk": {
                "value": character.stat_atk,
                "style": get_style(character.stat_atk, values_atk),
            },
            "stat_def": {
                "value": character.stat_def,
                "style": get_style(character.stat_def, values_def),
            },
            "stat_cr": {
                "value": character.stat_cr,
                "style": get_style(character.stat_cr, values_cr),
            },
            "stat_cd": {
                "value": character.stat_cd,
                "style": get_style(character.stat_cd, values_cd),
            },
            "stat_er": {
                "value": character.stat_er,
                "style": get_style(character.stat_er, values_er),
            },
            "stat_em": {
                "value": character.stat_em,
                "style": get_style(character.stat_em, values_em),
            },
            "cv": character.stat_cd + 2 * character.stat_cr,
        })
    # Sort by CV
    obj["characters"].sort(key=lambda x: x["cv"], reverse=True)
    return obj
