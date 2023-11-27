from django.urls import path, re_path
from . import views

urlpatterns = [

    path("", views.home),
    re_path("^" + "uid/(?P<uid>[0-9]{9})/" + "$", views.inspect),
    re_path("^" + "uid/(?P<uid1>[0-9]{9})/(?P<uid2>[0-9]{9})/" + "$", views.duel),
    path("how/", views.how),

    # -------------------------
    # /!\ Easter eggs below /!\
    # -------------------------

    path("uid/sex", views.easteregg_53x),

    # -------
    # Default
    # -------

    path("uid/<path:query>/", views.badquery),

]
