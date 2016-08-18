# Running the Orga Server

This is a step-by-step guide on how to run orga-server in your computer.


## Dependencies required to run Orga Server

* Python 2
* Postgres
* NodeJS


## Steps

Make sure you have the dependencies mentioned above installed before proceeding further.

Run the commands mentioned below with the terminal active in the project's root directory.


* **Step 1** - Install python requirements.

```sh
pip install -r requirements.txt
```


* **Step 2** - Create the database. For that we first open the psql shell.

```sh
sudo -u postgres psql
```

* When inside psql, create a user for open-event and then using the user create the database.

```sql
create user open_event_user with password 'test';
create database test with owner=open_event_user;
```

* Once database is created, exit the psql shell with `\q` followed by ENTER.


* **Step 3** - Install bower and frontend requirements. Learn more at [BOWER.md](BOWER.md)

```sh
npm install bower -g
bower install
```


* **Step 4** - Create application environment variables.

```sh
export DATABASE_URL=postgresql://open_event_user:start@127.0.0.1:5432/test
```


* **Step 5** - Start the postgres service.

```sh
sudo service postgresql restart
```


* **Step 6** - Create the tables. For that we will use `create_db.py`.

```sh
python create_db.py
# enter email and password
python manage.py db stamp head
```


* **Step 7** - Start the application along with the needed services.
The `&` at the end of the commands below make them run in background so that they don't hold the terminal. See [REDIS.md](REDIS.md) for more info.

```sh
# download and run redis
bash run_redis.sh
redis-3.2.1/src/redis-server &

# run worker
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
celery worker -A app.celery &
unset INTEGRATE_SOCKETIO

# run app
python manage.py runserver
```

* **Step 8** - Rejoice. Go to `localhost:5000` in your web browser to see the application live.
