#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Fix inconsistent migration history on Render caused by previous missing migrations
python manage.py shell -c "from django.db.migrations.recorder import MigrationRecorder; MigrationRecorder.Migration.objects.filter(app='chat', name='0002_alter_chatroom_options_alter_message_options_and_more').delete()" || true
python manage.py shell -c "from django.db.migrations.recorder import MigrationRecorder; MigrationRecorder.Migration.objects.filter(app='build', name__startswith='0003_builderprofile').delete()" || true

python manage.py migrate build --fake
python manage.py migrate chat --fake
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass') if not User.objects.filter(username='admin').exists() else None"
