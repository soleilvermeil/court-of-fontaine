from django.urls import path, re_path
from . import views

urlpatterns = [

    path("", views.home),
    re_path("^" + "uid/(?P<uid>[0-9]{9})/" + "$", views.inspect),
    path("uid/<slug:query>/", views.badquery),

    # -------------------------
    # /!\ Easter eggs below /!\
    # -------------------------

    path("uid/sex", views.easteregg_53x),

]
