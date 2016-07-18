#!/bin/bash
celery worker -A app.celery &
gunicorn app:app
# if not running on free dyno
# define a separate worker and scale
# https://devcenter.heroku.com/articles/celery-heroku
