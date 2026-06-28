#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

echo "MIGRATION_MODULES = {'chat': None}" >> conf/settings.py
python manage.py makemigrations build --name builderprofile
sed -i "/MIGRATION_MODULES = {'chat': None}/d" conf/settings.py
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass') if not User.objects.filter(username='admin').exists() else None"
