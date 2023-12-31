# Court of Fontaine

> Let yourself be judged.

A website that judges your artifacts, characters and your entire life.

## How to use

### Using Docker

You can use [Docker](https://www.docker.com) to compile all the files into an image (might take a few minutes):
```
docker build -t court-of-fontaine .
```

You can then run the image:
```
docker run -p 8000:8000 court-of-fontaine
```

You can then access the website at http://127.0.0.1:8000 **altough the terminal may indicate another URL** (this issue has still to be adressed; go to https://github.com/SoleilVermeil/court-of-fontaine/issues/1 to see if it has already been resolved).

### Run directly

If you know what you are doing, you can run the server directly. Go into the `django_project` folder. From there, if it is the first time, you will have to build the data base using the two very simple commands:
```
python manage.py makemigrations
python manage.py migrate
```
You can then run the server:
```
python manage.py runserver
```

You can then access the website at http://127.0.0.1:8000.
