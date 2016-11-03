#!/bin/bash
export REDIS_URL=redis://${REDIS_SERVICE_HOST}:${REDIS_SERVICE_PORT}/0
export DATABASE_URL=postgresql://postgres:test@${POSTGRES_SERVICE_HOST}:${POSTGRES_SERVICE_PORT}/opev
export SERVER_NAME=${WEB_SERVICE_HOST}
pwd
python manage.py initialize_db -c open_event_test_user@fossasia.org:fossasia # TODO. Temporary hack. will be removed
python manage.py db stamp $(python manage.py db heads | grep -o '^\S*') # TODO. Temporary hack. will be removed
bash docker_run.sh
