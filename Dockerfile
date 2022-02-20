# syntax=docker/dockerfile:1
FROM python:3.9.2
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Do migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Default datas
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=H687mRJCtQuRBZqW
ENV DJANGO_SUPERUSER_EMAIL=ahu1@babson.edu
RUN python manage.py createsuperuser
RUN python manage.py loaddata test_school.yaml test_user.yaml

# Run
CMD gunicorn -b localhost:8000 weplate.wsgi
