#!/bin/bash
export DATABASE_URL=postgresql://open_event_user:start@127.0.0.1:5432/test
postgres -D /usr/local/pgsql/data >logfile 2>&1 &
service postgresql restart
python create_db.py
python manage.py runserver -h 0.0.0.0 -p 5000
