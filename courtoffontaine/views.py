from django.shortcuts import render
from django.http import HttpResponse, Http404
from scripts import get_infos, reformat_infos, rate

def home(request):
    return render(request, "base_page_simpletext.html", {
        "title": "Welcome to the Court of Fontaine!",
        "body": "Enter your UID to be judged!"
    })

def inspect(request, uid):
    infos = get_infos(uid)
    try:
        infos = reformat_infos(infos)
        rating = rate(infos)
    except KeyError:
        return render(request, "base_page_simpletext.html", {
            "title": "You made Furina sad :c",
            "body": "No informations found for this UID.",
            "image": "sad.webp",
        })
    else:
        return render(request, "base_table.html", rating)

def badquery(request, query):
    return render(request, "base_page_simpletext.html", {
        "title": "Furina is making fun of you >v<",
        "body": "Please learn how to use a computer.",
        "image": "lol.webp",
    })

# -------------------------
# /!\ Easter eggs below /!\
# -------------------------

def easteregg_sex(request):
    return render(request, "base_page_simpletext.html", {
        "image": "secret.png",
    })