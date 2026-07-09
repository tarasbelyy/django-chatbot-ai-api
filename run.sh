#!/usr/bin/env sh

python manage.py migrate --noinput

DJANGO_SUPERUSER_USERNAME="admin" \
  DJANGO_SUPERUSER_PASSWORD="admin" \
  DJANGO_SUPERUSER_EMAIL="admin@example.com" \
  python manage.py createsuperuser --noinput

python manage.py runserver --noreload 0.0.0.0:8000