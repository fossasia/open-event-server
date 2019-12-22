#!/bin/sh
export DEPLOYMENT=${DEPLOYMENT:-api}

if
  [ "$1" = "run" ]
then
  echo "[LOG] Deploying ${DEPLOYMENT}"
  echo "[LOG] Using database: ${DATABASE_URL}"
  echo "[LOG] Using redis: ${REDIS_URL}"

  if [ "$2" = "" ]; then
    echo "[LOG] Waiting for Database" && ./scripts/wait-for.sh ${POSTGRES_HOST}:5432 --timeout=60 -- echo "[LOG] Database Up"
    echo "[LOG] Preparing database"
    python manage.py prepare_kubernetes_db
    echo "[LOG] Running migrations"
    python manage.py db upgrade
    export PORT=${PORT:-8080}
    export GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
    export GUNICORN_LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}
    echo "[LOG] Starting gunicorn on port ${PORT}"
    gunicorn -b 0.0.0.0:${PORT} app:app -w $GUNICORN_WORKERS --enable-stdio-inheritance --log-level $GUNICORN_LOG_LEVEL --proxy-protocol --preload $GUNICORN_EXTRA_ARGS
  fi

  if [ "$2" = "celery" ]; then
    echo "[LOG] Starting celery worker"
    export INTEGRATE_SOCKETIO=false
    export CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-info}
    celery worker -B -A app.celery --loglevel=$CELERY_LOG_LEVEL $CELERY_EXTRA_ARGS
  fi
fi
