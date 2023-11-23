from django.shortcuts import render
from django.http import HttpResponse, Http404
from scripts import get_infos, reformat_infos, rate

def home(request):
    return render(request, "base_page.html", {})

def inspect(request, uid):
    
    infos = get_infos(uid)
    try:
        infos = reformat_infos(infos)
        rating = rate(infos)
    except KeyError:
        raise Http404("Invalid UID")
    else:
        return render(request, "base_table.html", rating)