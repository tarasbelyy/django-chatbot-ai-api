#!/usr/bin/env sh

python manage.py collectstatic --noinput

python manage.py migrate --noinput

DJANGO_SUPERUSER_USERNAME="admin" \
  DJANGO_SUPERUSER_PASSWORD="admin" \
  DJANGO_SUPERUSER_EMAIL="admin@example.com" \
  python manage.py createsuperuser --noinput

gunicorn bot_constructor.wsgi:application --bind 0.0.0.0:8000
