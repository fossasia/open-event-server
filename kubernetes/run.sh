#!/bin/bash
export REDIS_URL=redis://${REDIS_SERVICE_HOST}:${REDIS_SERVICE_PORT}/0
export DATABASE_URL=postgresql://postgres:test@${POSTGRES_SERVICE_HOST}:${POSTGRES_SERVICE_PORT}/opev
pip install --no-cache-dir -r requirements.txt
bower install --allow-root && bower cache clean --allow-root
pwd
python manage.py initialize_db -c open_event_test_user@fossasia.org:fossasia # TODO. Temporary hack. will be removed
python manage.py db upgrade > /dev/null 2>&1
python manage.py db stamp head # TODO. Temporary hack. will be removed
bash docker_run.sh
