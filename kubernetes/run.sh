#!/bin/bash
apt-get update
apt-get install -y wget git ca-certificates curl && update-ca-certificates && apt-get clean -y
apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev git && apt-get clean -y
curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs && apt-get clean -y
npm install bower -g && npm cache clean
pip install --no-cache-dir -r requirements.txt
bower install --allow-root && bower cache clean --allow-root
export REDIS_URL=redis://${REDIS_SERVICE_HOST}:${REDIS_SERVICE_PORT}/0
export DATABASE_URL=postgresql://postgres:test@${POSTGRES_SERVICE_HOST}:${POSTGRES_SERVICE_PORT}/opev
export SERVER_NAME=${WEB_SERVICE_HOST}
pwd
python manage.py initialize_db -c open_event_test_user@fossasia.org:fossasia # TODO. Temporary hack. will be removed
python manage.py db stamp $(python manage.py db heads | grep -o '^\S*') # TODO. Temporary hack. will be removed
bash docker_run.sh
