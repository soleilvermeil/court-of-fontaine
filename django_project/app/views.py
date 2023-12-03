from django.shortcuts import render
from django.shortcuts import redirect
from .models import *
import random
from . import scriptsv2

def home(request):
    return render(request, "base_page_simpletext.html", {
        "title": "Welcome to the Court of Fontaine!",
        "body": "Enter your UID to be judged!"
    })

def inspect(request, uid):
    infos = scriptsv2.add_player(uid)
    obj = scriptsv2.get_player(uid, include_rating=True)
    print(obj)

    return render(request, "base_table.html", obj)




def inspectrandom(request):
    uid = random.randint(100000000, 999999999)
    uid = str(uid)
    uid = uid[0] + "0" + uid[2:]
    uid = int(uid)
    return inspect(request, uid)

def duel(request, uid1, uid2):

    return render(request, "base_page_simpletext.html", {
        "title": "You made Furina sad T-T",
        "body": f"Coming soon...",
        "image": "sad.webp",
        "imagewidth": "1/10",
    })


    # infos_1 = scripts.get_infos(uid1)
    # infos_2 = scripts.get_infos(uid2)
    # ratings = {"player_1": {}, "player_2": {}}
    # nicknames = [None] * 2
    # for i, infos_ in enumerate([infos_1, infos_2]):
    #     try:
    #         nickname = infos_["playerInfo"]["nickname"]
    #         uid = infos_["uid"]
    #         nicknames[i] = nickname
    #         infos = scripts.reformat_infos(infos_)
    #         infos = scripts.combine_infos(infos)
    #         rating = scripts.rate(infos)
    #     except KeyError:
    #         return render(request, "base_page_simpletext.html", {
    #             "title": "You made Furina sad T-T",
    #             "body": f"It seems that '{uid}' don't want to be judged.",
    #             "image": "sad.webp",
    #             "imagewidth": "1/10",
    #         })
    #     except TypeError:
    #         return render(request, "base_page_simpletext.html", {
    #             "title": "You made Furina sad T-T",
    #             "body": f"It seems that '{uid}' doesn't exist.",
    #             "image": "sad.webp",
    #             "imagewidth": "1/10",
    #         })
    #     else:
    #         scripts.save(infos, "infos")
    #         scripts.save(rating, "rating")
    #         ratings[f"player_{i + 1}"] = rating
    # names_1 = [character["name"] for character in ratings["player_1"]["characters"]]
    # names_2 = [character["name"] for character in ratings["player_2"]["characters"]]
    # names_intersection = list(set(names_1) & set(names_2))
    # ratings["player_1"]["characters"] = [character for character in ratings["player_1"]["characters"] if character["name"] in names_intersection]
    # ratings["player_2"]["characters"] = [character for character in ratings["player_2"]["characters"] if character["name"] in names_intersection]
    # if len(names_intersection) > 0:
    #     return render(request, "base_table_duel.html", {
    #         "characters": zip(ratings["player_1"]["characters"], ratings["player_2"]["characters"]),
    #         "nickname_1": nicknames[0],
    #         "nickname_2": nicknames[1],
    #         "uid_1": uid1,
    #         "uid_2": uid2,
    #     })
    # else:
    #     return render(request, "base_page_simpletext.html", {
    #         "title": "You made Furina sad T-T",
    #         "body": "The two players have no characters in common.",
    #         "image": "sad.webp",
    #         "imagewidth": "1/10",
    #     })
    

def badquery(request, query):
    return render(request, "base_page_simpletext.html", {
        "title": "Furina is making fun of you >v<",
        "body": "Please learn how to use a computer.",
        "image": "lol.webp",
        "imagewidth": "1/10",
    })

def how(request):
    return render(request, "base_page_simpletext.html", {
        "title": "How are we judged?",
        "body": "You'll know soon enough...",
        "image": "knife.webp",
        "imagewidth": "1/10",
    })

def char(request, name):

    return render(request, "base_page_simpletext.html", {
        "title": "You made Furina sad T-T",
        "body": f"Coming soon...",
        "image": "sad.webp",
        "imagewidth": "1/10",
    })
    # TODO: Remove this in the future
    # if " " in name:
    #     return redirect(f"/char/{name.replace(' ', '_')}/")
    # ratings, infos = scripts.get_ratings_of_character(name)
    # print(ratings)
    # print(infos)
    # users = [r["nickname"] for r in ratings]

    # substats = ["ATK%", "DEF%", "HP%", "Energy Recharge", "Elemental Mastery", "Crit DMG", "Crit RATE"]
    
    # data = [
    #     {
    #         "uid": user['uid'],
    #         "nickname": user['nickname'],
    #         "progress": user['characters'][0]['progress'],
    #         "stats": {
    #             stat: 0
    #         for stat in substats},
    #     }
    #     for user in ratings
    # ]
    
    # artifact_types = ["flower", "feather", "sands", "goblet", "circlet"]

    # for i, (rating, info) in enumerate(zip(ratings, infos)):
    #     print(info['nickname'])
    #     for substat in substats:
    #         x = 0
    #         for artifact_type in artifact_types:
    #             try:
    #                 dx = scripts.get_substat_value(substat_name=substat, artifact_substats=info['characters'][0]['artifacts'][artifact_type]['substats'])
    #                 x += dx
    #                 if info['characters'][0]['artifacts'][artifact_type]['mainstat']['name'] == substat:
    #                     x += info['characters'][0]['artifacts'][artifact_type]['mainstat']['value']
    #             except KeyError:
    #                 pass
    #         # print(f"{substat}: {x:.1f}")
    #         x = round(x, 1)
    #         data[i]['stats'][substat] = f"{x:.1f}"
    
    # print(data)

    # return render(request, "base_table_leaderboard.html", {"players": data})


# -------------------------
# /!\ Easter eggs below /!\
# -------------------------

def easteregg_53x(request):
    return render(request, "base_page_simpletext.html", {
        "title": f"This one was easy...",
        "body": f"...but can you find the other ones?",
        "image": "eastereggs/53x.png",
        "imagewidth": "1/3",
        "nsfw": True,
    })


def easteregg_nuk3(request):
    return render(request, "base_page_simpletext.html", {
        "title": "Je vous laisse deux options...",
        "body": "Soit vous m'en achetez un, soit je vous nuke.",
        "image": "eastereggs/nuk3.jpg",
        "imagewidth": "1/3",
    })

def easteregg_k0n4m1(request):
    return render(request, "base_page_simpletext.html", {
        "title": "You are a true gamer!",
        "body": "Here's a little reward.",
        "image": "eastereggs/k0n4m1.png",
        "imagewidth": "1/3",
        "nsfw": True,
    })


def easteregg_b1rth(request):
    return render(request, "base_page_simpletext.html", {
        "title": "You remembered Furina's birthday!",
        "body": "However today's gift is for you.",
        "image": "eastereggs/b1rth.png",
        "imagewidth": "1/3",
        "nsfw": True,
    })


