#!/bin/bash
export INTEGRATE_SOCKETIO=false
celery worker -A app.celery --loglevel=info &
unset INTEGRATE_SOCKETIO
gunicorn -b 0.0.0.0:5000 app:app --worker-class eventlet -w 1
