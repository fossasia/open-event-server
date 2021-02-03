# Generic

## Dependencies required to run Orga Server

* Python 3.8
* PostgreSQL
* Redis


```sh
xargs -a deb-packages.txt sudo apt install
```

## Steps

Make sure you have the dependencies mentioned above installed before proceeding further.

Run the commands mentioned below with the terminal active in the project's root directory.


* **Step 1** - Install Poetry and Python 3 requirements.

This project uses [Poetry](https://python-poetry.org/docs) to handle Python dependencies.

```sh
# Install Poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
source ~/.profile

# Install Python dependencies
poetry install

# Activate virtual environment
poetry shell
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

Add `SECRET_KEY={{something random}}` in .env file for cryptographic usage. Note that server will not run in production mode if you don't supply a secret.
To get a good secret value, run `python -c 'import secrets;print(secrets.token_hex())'` in a terminal and replace `{{something random}}` with its output in the line above in `.env` file


* **Step 4** - Start the postgres service.

```sh
sudo service postgresql restart
```


* **Step 5** - Create the tables. For that we will use `flask create_db`.

```sh
flask create_db
# enter email and password
flask db stamp head
```


* **Step 6** - Start the application along with the needed services.

```sh
# run worker
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
celery -A app.instance.celery worker -B -l INFO -c 2 &
unset INTEGRATE_SOCKETIO

# run app
flask run
```

* **Step 7** - Rejoice. Go to `localhost:5000` in your web browser to see the application live.
