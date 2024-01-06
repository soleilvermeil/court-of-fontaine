# Court of Fontaine

Let yourself be judged!

![Website overview](https://github.com/SoleilVermeil/court-of-fontaine/assets/100100316/9cf40331-6113-49be-9b2e-40d34e3565e2)

## How to use

### Using Docker (recommended)

You can use [Docker](https://www.docker.com) to run the container containing all necessary files. To do so, you will need an image which you can either [download](https://github.com/SoleilVermeil/court-of-fontaine/releases/latest) or build yourself using
```
docker build -t court-of-fontaine .
```
If you decide to build it yourself, you can optionaly retrieve the freshly built image using
```
docker save -o court-of-fontaine.tar court-of-fontaine
```
Once the image has been downloaded or built, you have to run a container from this image using the following command, while specifying the (absolute !) path of the folder where the database shall be stored, using
```
docker run -v <database folder>:/db -p 8000:8000 court-of-fontaine
```

You can then access the website at `http://<ip address>:8000` (or `http://localhost:8000` if you are running the container from your computer).

### Using Python (not recommended)

If you know what you are doing, you can run the server directly from source code. Note that this project has been developped in [Python `3.11.7`](https://www.python.org/downloads/release/python-3117/). To run the application, you will first need to install some modules. You can install them all at once by going into the project's root folder (in which there is `requirements.txt`) and run
```
pip install -r requirements.txt
```
Once this is done, you should be able to run the application. To do so, go into the `app` folder (in which there is `manage.py`). From there, if it is your first time executing this code, you will have to build the database and some other stuff using
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```
You can then run the server using
```
python manage.py runserver
```
You can then access the website at `http://localhost:8000`.
