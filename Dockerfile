FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/django_project

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]