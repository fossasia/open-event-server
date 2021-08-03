#!/bin/bash
chmod -R 0777 ./static &
./scripts/l10n.sh generate &
touch .env &
celery -A app.instance.celery worker --loglevel=info -c 1 &
if [ "$APP_CONFIG" = "config.DevelopmentConfig" ]; then
    python manage.py runserver -h 0.0.0.0 -p ${PORT:-8000} --no-reload
else
    gunicorn app.instance:app -w 1
fi
# if not running on free dyno
# define a separate worker and scale
# https://devcenter.heroku.com/articles/celery-heroku
