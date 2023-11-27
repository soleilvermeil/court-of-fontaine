from django.shortcuts import render
import scripts

def home(request):
    return render(request, "base_page_simpletext.html", {
        "title": "Welcome to the Court of Fontaine!",
        "body": "Enter your UID to be judged!"
    })

def inspect(request, uid):
    infos = scripts.get_infos(uid)
    try:
        nickname = infos["playerInfo"]["nickname"]
        infos = scripts.reformat_infos(infos)
        infos = scripts.combine_infos(infos)
        rating = scripts.rate(infos)
    except KeyError:
        return render(request, "base_page_simpletext.html", {
            "title": "You made Furina sad T-T",
            "body": "It seems that the player don't want to be judged.",
            "image": "sad.webp",
        })
    except TypeError:
        return render(request, "base_page_simpletext.html", {
            "title": "You made Furina sad T-T",
            "body": "It seems that this UID doesn't exist.",
            "image": "sad.webp",
        })
    else:
        scripts.save(infos)
        return render(request, "base_table.html", rating | {"title": nickname, "body": uid})

def duel(request, uid1, uid2):
    infos_1 = scripts.get_infos(uid1)
    infos_2 = scripts.get_infos(uid2)
    ratings = {"player_1": {}, "player_2": {}}
    nicknames = [None] * 2
    uids = [None] * 2
    for i, infos_ in enumerate([infos_1, infos_2]):
        try:
            nickname = infos_["playerInfo"]["nickname"]
            nicknames[i] = nickname
            infos = scripts.reformat_infos(infos_)
            infos = scripts.combine_infos(infos)
            rating = scripts.rate(infos)
        except KeyError:
            return render(request, "base_page_simpletext.html", {
                "title": "You made Furina sad T-T",
                "body": "It seems that one of the players don't want to be judged.",
                "image": "sad.webp",
            })
        except TypeError:
            return render(request, "base_page_simpletext.html", {
                "title": "You made Furina sad T-T",
                "body": "It seems that one of those UIDs doesn't exist.",
                "image": "sad.webp",
            })
        else:
            scripts.save(infos)
            ratings[f"player_{i + 1}"] = rating
    names_1 = [character["name"] for character in ratings["player_1"]["characters"]]
    names_2 = [character["name"] for character in ratings["player_2"]["characters"]]
    names_intersection = list(set(names_1) & set(names_2))
    ratings["player_1"]["characters"] = [character for character in ratings["player_1"]["characters"] if character["name"] in names_intersection]
    ratings["player_2"]["characters"] = [character for character in ratings["player_2"]["characters"] if character["name"] in names_intersection]
    if len(names_intersection) > 0:
        return render(request, "base_table_duel.html", {
            "characters": zip(ratings["player_1"]["characters"], ratings["player_2"]["characters"]),
            "nickname_1": nicknames[0],
            "nickname_2": nicknames[1],
            "uid_1": uid1,
            "uid_2": uid2,
        })
    else:
        return render(request, "base_page_simpletext.html", {
            "title": "You made Furina sad T-T",
            "body": "The two players have no characters in common.",
            "image": "sad.webp",
        })
    

def badquery(request, query):
    return render(request, "base_page_simpletext.html", {
        "title": "Furina is making fun of you >v<",
        "body": "Please learn how to use a computer.",
        "image": "lol.webp",
    })

def how(request):
    return render(request, "base_page_simpletext.html", {
        "title": "How are we judged?",
        "body": "You'll know soon enough...",
        "image": "knife.webp",
    })


# -------------------------
# /!\ Easter eggs below /!\
# -------------------------

def easteregg_53x(request):
    return render(request, "base_page_simpletext.html", {
        "image": "easteregg_53x.png",
    })