#!/bin/bash
echo "Deploying ${DEPLOYMENT}"
export REDIS_URL=redis://${REDIS_SERVICE_HOST}:${REDIS_SERVICE_PORT}/0
export DATABASE_URL=postgresql://postgres:test@${POSTGRES_SERVICE_HOST}:${POSTGRES_SERVICE_PORT}/opev
pip install --no-cache-dir -r requirements.txt
if [ "$DEPLOYMENT" == "web" ]
then
    bower install --allow-root && bower cache clean --allow-root
fi
pwd
python manage.py initialize_db -c open_event_test_user@fossasia.org:fossasia # TODO. Temporary hack. will be removed
python manage.py db upgrade > /dev/null 2>&1
python manage.py db stamp head # TODO. Temporary hack. will be removed
if [ "$DEPLOYMENT" == "web" ]
then
    gunicorn -b 0.0.0.0:5000 app:app --worker-class eventlet -w 1
fi
if [ "$DEPLOYMENT" == "celery" ]
then
    export INTEGRATE_SOCKETIO=false
    celery worker -A app.celery --loglevel=debug
fi
