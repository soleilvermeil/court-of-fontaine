from django.shortcuts import render
from django.shortcuts import redirect
from .models import *
import random
from . import scripts


def home(request):
    return render(request, "base_page_simpletext.html", {
        "title": "Welcome to the Court of Fontaine!",
        "body": "Enter your UID to be judged!"
    })


def inspect(request, uid):
    try:
        scripts.add_player(uid, return_avatar=True)
    except AssertionError as e:
        return notfound(request, e)
    obj = scripts.get_player(uid, include_rating=True)
    nickname = obj["nickname"]
    avatar = obj["avatar"]
    return render(request, "base_table.html", obj | {
        'title': nickname,
        'body': uid,
        'image_url': avatar,
        'imagewidth': '32',
    })


def inspectrandom(request):
    uid = random.randint(1e8, 1e9 - 1)
    return inspect(request, uid)


def duel(request, uid1, uid2):
    return render(request, "base_page_simpletext.html", {
        "title": "You made Furina sad T-T",
        "body": f"Coming soon...",
        "image": "sad.webp",
        "imagewidth": "32",
    })


def notfound(request, query = None):
    if query is None:
        query = "Could not find the page you were looking for."
    return render(request, "base_page_simpletext.html", {
        "title": "You made Furina sad T-T",
        "body": query,
        "image": "sad.webp",
        "imagewidth": "32",
    })


def badquery(request, query):
    return render(request, "base_page_simpletext.html", {
        "title": "Furina is making fun of you >v<",
        "body": "Please learn how to use a computer.",
        "image": "lol.webp",
        "imagewidth": "32",
    })
    

def how(request):
    return render(request, "base_page_simpletext.html", {
        "title": "What determines the judgment?",
        "body": "We don't care about your skills or your builds, only your luck matters.",
        "image": "knife.webp",
        "imagewidth": "32",
    })
    

def char(request, name):
    return render(request, "base_page_simpletext.html", {
        "title": "You made Furina sad T-T",
        "body": f"Coming soon...",
        "image": "sad.webp",
        "imagewidth": "32",
    })


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
