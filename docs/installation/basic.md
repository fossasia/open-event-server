# Generic

## Dependencies required to run Orga Server


* Python 3.8
* Postgres
* OpenSSL

### For mac users
```sh
brew install postgresql
```

### For debian-based linux users
```sh
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib libssl-dev
xargs -a deb-packages.txt sudo apt install
```

## Steps

Make sure you have the dependencies mentioned above installed before proceeding further.

Run the commands mentioned below with the terminal active in the project's root directory.

* **Step 0** - Clone the Open Event Server repository (from the development branch) and ```cd ``` into the directory.
```sh
git clone -b development https://github.com/fossasia/open-event-server.git
cd open-event-server
```
**Note :** If you want to contribute, first fork the original repository and clone the forked repository into your local machine followed by ```cd``` into the directory
```sh
git clone https://github.com/USERNAME/open-event-server.git
cd open-event-server
```

* **Step 1** - Install python3 requirements. You need to be present in the root directory of the project.

# Installation in Virtual Environment

*Note:* This is recommended over the system wide installation.

Firstly, open a terminal and enter

```sh
# For linux users
sudo apt-get install python3-dev
sudo apt-get install libpq-dev
sudo apt-get install libffi6 libffi-dev

# For macOS users
brew install python@3
brew install libmagic
```

## Using pip and virtualenv

Open a terminal and enter the following commands to setup a virtual environment

* **Step 1** - Install Poetry and Python 3 requirements.

This project uses [Poetry](https://python-poetry.org/docs) to handle Python dependencies.

```sh
# Install Poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
source ~/.profile

# Activate virtual environment
poetry shell

# Install Python dependencies
poetry install
```



* **Step 2** - Create the database. For that we first open the psql shell. Go to the directory where your postgres file is stored.

```sh
# For linux users
sudo -u postgres psql

# For macOS users
psql -d postgres
```

* When inside psql, create a user for open-event and then using the user create the database. Also, create a test database named opev_test for the test suites by dumping the oevent database into it. without this, the tests will not run locally.

For ease of development, you should create Postgres user with the same username as your OS account. If your OS login account is _john_, for example, you should create _john_ user in Postgres. By this, you can skip entering password when using database.

```sql
CREATE USER open_event_user WITH PASSWORD 'opev_pass';
CREATE DATABASE oevent WITH OWNER open_event_user;
```

* Once the databases are created, exit the psql shell with `\q` followed by ENTER.*



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
for mac users:

```sh
brew services restart postgresql
```

* **Step 5** - Create the tables. For that we will use `create_db.py`.

```sh
python3 create_db.py
# enter email and password
python3 manage.py db stamp head
```

**Note 1:** For  Mac OS, in case you encounter `Library not loaded: /usr/local/opt/libffi/lib/libffi.6.dylib` , run
```commandline
brew install libffi
For compilers to find libffi you may need to set:
export LDFLAGS="-L/usr/local/opt/libffi/lib"
export CPPFLAGS="-I/usr/local/opt/libffi/include"
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
```
**OR**

you encounter `OSError: cannot load library 'pango-1.0': dlopen(pango-1.0, 2): image not found.  Additionally, ctypes.util.find_library() did not manage to locate a library called 'pango-1.0'`
```commandline
brew install pango
```

**Note 2:** In case you made your own username and password in Step 2 are now getting `FATAL:  password authentication failed for user "john"` , probable cause is non updation of `.env` file. To resolve it, open the `.env` file and update `DATABASE_URL=postgresql://USERNAME:PASSWORD@127.0.0.1:5432/oevent` and you are good to go.

**Note 3:** In case you are using Anaconda distribution for python, you may get an import error regarding `celery.signals` module. Please use the default python version while executing these steps in that case.

* **Step 6** - Start the application along with the needed services.

```sh

# Install and run redis
# For Ubuntu, Debian and alike
sudo apt-get install redis-server
# For Fedora, RedHat, CentOS
sudo dnf install redis
# For macOS
brew install redis
brew services start redis

# run worker
export INTEGRATE_SOCKETIO=false
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
celery -A app.instance.celery worker -B -l INFO -c 2 &
unset INTEGRATE_SOCKETIO

# run app
python3 manage.py runserver
```

* **Step 7** - Rejoice. Go to `localhost:5000` in your web browser to see the application live.


## Flask-SocketIO development

[Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) has been used in the project for displaying real-time notifications to the user. Although it's switched off by default. To integrate SocketIO you must set the `INTEGRATE_SOCKETIO` variable to `true` at bash.

```bash
export INTEGRATE_SOCKETIO="true"
```

The development server is the one that Flask ships with. It's based on Werkzeug and does not support WebSockets. If you try to run it, you'll get a RunTime error, something like: `You need to use the eventlet server. `.  To test real-time notifications, you must use the Gunicorn web server with eventlet worker class.

If you've installed development requirements, you should have both `gunicorn` and `eventlet` installed. To run application on port 5000, execute the following instead of `python3 manage.py runserver`:

```bash
gunicorn app.instance:app --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload
```
* **Deployment**

### Nginx

Gunicorn shouldn't be serving static files, it's supposed to run just the Flask application. You can use [Nginx](https://www.nginx.com/) to serve static files and bypass other requests to the Gunicorn server, using it as a reverse proxy server. Proper configuration to enable proxying of WebSocket requests can be found in the Flask-SocketIO documentation: https://flask-socketio.readthedocs.io/en/latest/ (search for Nginx).

#### For Vagrant Machine

Doing the same for Vagrant machine requires some more configuration. If you're using the `Vagrantfile` provided in the repo, then you can check that the port forwarding is done as: 8001 -> 5000. So accessing the 8001 port in host machine will access the port 5000 in the guest (vagrant) machine. So in the guest machine, you need to run Nginx at port 5000 and gunicorn at some other port (let's assume port 5001).

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen       5000;

    sendfile off;

    location /static {
        alias /vagrant/app/static;
    autoindex on;
    }

    location / {
    proxy_pass http://127.0.0.1:5001;

    proxy_redirect http://127.0.0.1:5001/ http://127.0.0.1:8001/;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    break;
    }
}
```

You can directly use this configuration and put it inside sites-available (`/etc/nginx/sites-available/nginx.conf`) and create a symlink for it in sites-enabled (`/etc/nginx/sites-enabled/nginx.conf`).

Test the Nginx configuration and restart the Nginx server. Then run the Gunicorn server.

```bash
sudo service nginx testconfig # Should respond with "test is successful"
sudo service nginx restart
gunicorn app.instance:app --worker-class eventlet -w 1 --bind 0.0.0.0:5001 --reload
```

