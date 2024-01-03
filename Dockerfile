FROM python:3.11-alpine3.19
LABEL maintainer="SoleilVermeil"
ENV PYTHONUNBUFFERED=1
ENV RUNNING_IN_DOCKER=1

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./app /app
WORKDIR /app

EXPOSE 8000
VOLUME /db

CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "collectstatic --noinput"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]