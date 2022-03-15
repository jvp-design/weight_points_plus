#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements/production.txt

python manage.py collectstatic --no-input --settings=mysite.settings.production
python manage.py migrate --settings=mysite.settings.production
