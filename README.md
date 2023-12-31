# Court of Fontaine
A website that judges your artifacts.

## How to use

### Using Docker

You can use the Docker to compile all the files into an image (might take a few minutes):
```
docker build -t court-of-fontaine .
```

You can then run the image:
```
docker run -p 8000:8000 court-of-fontaine
```

You can then access the website at http://127.0.0.1:8000 **altough the terminal may indicate another URL**.

### Run directly

If you know what you are doing, you can run the server directly. Go into the `django_project` folder. From there, run the following commands:
```
python manage.py runserver
```

You can then access the website at http://127.0.0.1:8000.