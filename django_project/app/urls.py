from django.urls import path, re_path
from . import views

urlpatterns = [

    path("", views.home),
    re_path("^" + "uid/(?P<uid>[0-9]{9})/" + "$", views.inspect),
    re_path("^" + "uid/(?P<uid1>[0-9]{9})/(?P<uid2>[0-9]{9})/" + "$", views.duel),
    path("uid/random/", views.inspectrandom),
    path("how/", views.how),
    path("char/<str:name>/", views.char),

    # -------------------------
    # /!\ Easter eggs below /!\
    # -------------------------

    path("uid/sex/", views.easteregg_53x),
    path("uid/nuke/", views.easteregg_nuk3),
    path("uid/uuddlrlrba/", views.easteregg_k0n4m1),
    path("uid/1310/", views.easteregg_b1rth),

    # -------
    # Default
    # -------

    path("uid/<path:query>/", views.badquery),

]
