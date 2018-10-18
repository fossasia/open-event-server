#!/bin/sh
export DEPLOYMENT=${DEPLOYMENT:-api}

echo "[LOG] Deploying ${DEPLOYMENT}"
echo "[LOG] Using database: ${DATABASE_URL}"
echo "[LOG] Using redis: ${REDIS_URL}"

if [ "$DEPLOYMENT" == "api" ]
then
    echo "[LOG] Preparing database"
    python manage.py prepare_kubernetes_db
    echo "[LOG] Running migrations"
    python manage.py db upgrade
    export PORT=${PORT:-8080}
    echo "[LOG] Starting gunicorn on port ${PORT}"
    gunicorn -b 0.0.0.0:${PORT} app:app -w 1 --enable-stdio-inheritance --log-level "warning" --proxy-protocol
fi
if [ "$DEPLOYMENT" == "celery" ]
then
    echo "[LOG] Starting celery worker"
    export INTEGRATE_SOCKETIO=false
    celery worker -A app.celery --loglevel=warning
fi
