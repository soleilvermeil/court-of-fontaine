# Court of Fontaine

> Let yourself be judged.

A website that judges your artifacts, characters and your entire life.

## How to use

### Using Docker

You can use [Docker](https://www.docker.com) to compile all the files into an image:
```
docker build -t court-of-fontaine .
```
Optionally, you can retrieve the freshly built image:
```
docker save -o court-of-fontaine.tar court-of-fontaine
```
You can then run the image, specifying the (absolute) path of the folder where the database will be stored:
```
docker run -v {absolute path to db folder}:/db -p 8000:8000 court-of-fontaine
```

You can then access the website at http://127.0.0.1:8000 altough the terminal may indicate another URL (this issue has still to be adressed; see [this issue](https://github.com/SoleilVermeil/court-of-fontaine/issues/1) to check for updates).

### Run directly

If you know what you are doing, you can run the server directly. Go into the `django_project` folder. From there, if it is the first time, you will have to build the data base using the two very simple commands:
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```
You can then run the server:
```
python manage.py runserver
```
You can then access the website at http://127.0.0.1:8000.
