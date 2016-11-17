#!/bin/bash
echo "Deploying ${DEPLOYMENT}"
export REDIS_URL=redis://${REDIS_SERVICE_HOST}:${REDIS_SERVICE_PORT}/0
export DATABASE_URL=postgresql://postgres:test@${POSTGRES_SERVICE_HOST}:${POSTGRES_SERVICE_PORT}/opev
python manage.py initialize_db -c open_event_test_user@fossasia.org:fossasia
python manage.py db upgrade > /dev/null 2>&1
if [ "$DEPLOYMENT" == "web" ]
then
    gunicorn -b 0.0.0.0:5000 app:app --worker-class eventlet -w 1
fi
if [ "$DEPLOYMENT" == "celery" ]
then
    export INTEGRATE_SOCKETIO=false
    celery worker -A app.celery --loglevel=debug
fi
