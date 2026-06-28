#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

echo "MIGRATION_MODULES = {'chat': None}" >> conf/settings.py
python manage.py makemigrations build --name builderprofile
sed -i "/MIGRATION_MODULES = {'chat': None}/d" conf/settings.py
python manage.py migrate
