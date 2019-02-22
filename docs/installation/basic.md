# Generic

## Dependencies required to run Orga Server

* Python 3
* Postgres
```sh
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

## Steps

Make sure you have the dependencies mentioned above installed before proceeding further.

Run the commands mentioned below with the terminal active in the project's root directory.


* **Step 1** - Install Python 3 requirements.

```sh
pip3 install -r requirements.txt
```


* **Step 2** - Create the database. For that we first open the psql shell.

```sh
sudo -u postgres psql
```

* When inside psql, create a user for open-event and then using the user create the database.

```sql
CREATE USER open_event_user WITH PASSWORD 'opev_pass';
CREATE DATABASE oevent WITH OWNER open_event_user;
```

* Once database is created, exit the psql shell with `\q` followed by ENTER.


* **Step 3** - Create application environment variables.

```sh
cp .env.example .env
```


* **Step 4** - Start the postgres service.

```sh
sudo service postgresql restart
```


* **Step 5** - Create the tables. For that we will use `create_db.py`.

```sh
python3 create_db.py
# enter email and password
python3 manage.py db stamp head
```


* **Step 6** - Start the application along with the needed services.
The `&` at the end of the commands below make them run in background so that they don't hold the terminal.

```sh
# download and run redis
wget http://download.redis.io/releases/redis-3.2.1.tar.gz
tar xzf redis-3.2.1.tar.gz
rm redis-3.2.1.tar.gz
cd redis-3.2.1
make

# To run redis
redis-3.2.1/src/redis-server &

# run worker
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
celery worker -A app.celery &
unset INTEGRATE_SOCKETIO

# run app
python3 manage.py runserver
```

* **Step 7** - Rejoice. Go to `localhost:5000` in your web browser to see the application live.
