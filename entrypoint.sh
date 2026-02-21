#!/usr/bin/env bash
set -e

python manage.py collectstatic --no-input --settings=config.settings.production
python manage.py makemigrations admin_honeypot --settings=config.settings.production
python manage.py migrate --settings=config.settings.production

exec gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}
