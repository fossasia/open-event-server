#!/bin/bash
echo "[LOG] Deploying ${DEPLOYMENT}"
echo "[LOG] Using database: ${DATABASE_URL}"
echo "[LOG] Using redis: ${REDIS_URL}"
if [ "$DEPLOYMENT" == "api" ]
then
    echo "[LOG] Preparing database"
    python manage.py prepare_db
    echo "[LOG] Running migrations"
    python manage.py db upgrade
    echo "[LOG] Starting gunicorn on port 8080"
    gunicorn -b 0.0.0.0:8080 app.instance:app -w 1 --enable-stdio-inheritance --log-level "warning" --proxy-protocol
fi
if [ "$DEPLOYMENT" == "celery" ]
then
    echo "[LOG] Starting celery worker"
    export INTEGRATE_SOCKETIO=false
    celery -A app.instance.celery worker -B --loglevel=warning
fi
