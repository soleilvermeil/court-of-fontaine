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
            "body": "No informations found for this UID.",
            "image": "sad.webp",
        })
    else:
        scripts.save(infos)
        return render(request, "base_table.html", rating | {"title": nickname, "body": uid})

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