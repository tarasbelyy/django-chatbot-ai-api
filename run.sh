#!/usr/bin/env sh

python manage.py collectstatic --noinput

python manage.py migrate --noinput

DJANGO_SUPERUSER_USERNAME="admin" \
  DJANGO_SUPERUSER_PASSWORD="admin" \
  DJANGO_SUPERUSER_EMAIL="admin@example.com" \
  python manage.py createsuperuser --noinput

gunicorn bot_constructor.asgi:application -k uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000
