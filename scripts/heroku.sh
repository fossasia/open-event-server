#!/bin/bash
python3 manage.py db upgrade
python3 populate_db.py
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
chmod -R 0777 ./static
celery worker -A app.instance.celery --loglevel=info &
if [ "$APP_CONFIG" = "config.DevelopmentConfig" ]; then
    python manage.py runserver -h 0.0.0.0 -p ${PORT:-8000} --no-reload
else
    gunicorn app.instance:app -w 1
fi
# if not running on free dyno
# define a separate worker and scale
# https://devcenter.heroku.com/articles/celery-heroku
