#!/bin/bash
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
celery worker -A app.celery --loglevel=info &
unset INTEGRATE_SOCKETIO
gunicorn app:app --worker-class eventlet -w 1
# if not running on free dyno
# define a separate worker and scale
# https://devcenter.heroku.com/articles/celery-heroku
