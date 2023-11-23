from django.shortcuts import render

def home(request):
    return render(request, "base_table.html", {
        "BGAUTHORNAME": "Hello world",
        "BGAUTHORLINK": "google.com",
        "uid": "703047530",
        "datetime": "2023-11-21T17:48:27.420307",
        "characters": [
            {
                "name": "Furina",
                "artifacts": {
                    "flower": {
                        "rating": {
                            "text": "Excellent",
                            "textcolor": "green-900",
                            "bgcolor": "green-500",
                        },
                        "tooltips": [
                            {
                                "text": "Good CRIT value",
                                "textcolor": "green-700",
                                "textweight": "bold",
                            },
                            {
                                "text": "Excellent substats",
                                "textcolor": "green-700",
                                "textweight": "normal",
                            },
                            {
                                "text": "Bad rolls",
                                "textcolor": "red-700",
                                "textweight": "normal",
                            },
                        ]
                    },
                    "feather": {
                        "rating": {
                            "text": "Bad",
                            "textcolor": "red-700",
                            "bgcolor": "red-200",
                        },
                        "tooltips": [
                            {
                                "text": "Good CRIT value",
                                "textcolor": "green-700",
                                "textweight": "bold",
                            },
                            {
                                "text": "Excellent substats",
                                "textcolor": "green-700",
                                "textweight": "normal",
                            },
                            {
                                "text": "Bad rolls",
                                "textcolor": "red-700",
                                "textweight": "normal",
                            },
                        ]
                    },
                }
            }
        ]
    })