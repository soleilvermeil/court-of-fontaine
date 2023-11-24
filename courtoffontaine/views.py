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
            "body": "No informations found for this UID."
        })
    else:
        return render(request, "base_table.html", rating)