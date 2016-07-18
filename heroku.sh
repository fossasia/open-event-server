#!/bin/bash
celery worker -A open_event.celery &
gunicorn open_event:app
# if not running on free dyno
# define a separate worker and scale
# https://devcenter.heroku.com/articles/celery-heroku
