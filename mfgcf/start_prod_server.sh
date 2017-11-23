#!/usr/bin/env bash

export DJANGO_SETTINGS_MODULE=mfgcf.settings_prod

. ../../venv/mfgcf/bin/activate
python manage.py collectstatic --no-input
exec gunicorn mfgcf.wsgi -w 5 --user=mfgcf --group=mfgcf
