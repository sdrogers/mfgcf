#!/usr/bin/env bash

. ../../venv/mfgcf/bin/activate
set -a
. .env
set +a
python manage.py collectstatic --no-input
exec gunicorn mfgcf.wsgi -w 5 --user=mfgcf --group=mfgcf
