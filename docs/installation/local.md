# Local

## Dependencies required to run Orga Server

-   Python 3.7
-   Postgres
-   OpenSSL

## Get a copy of source code

- Clone the Open Event Server repository (from the development branch) and `cd ` into the directory.

```sh
git clone https://github.com/fossasia/open-event-server.git
cd open-event-server
```

- If you want to contribute, first fork the original repository to your GitHub profile and clone that fork into your local machine, followed by `cd` into the directory

```sh
git clone git@github.com:USERNAME/open-event-server.git
cd open-event-server
```

- Tip:

  + Setup SSH key in your profile, and use SSH method to clone the source code, so that you don't have to type password repeatly.

  + To let your personal fork up-to-date with the original FOSSASIA repo, add original repo to "remote" list and regularly fetch its new content.

  ```sh
  git remote add upstream https://github.com/fossasia/open-event-server.git
  git fetch upstream
  git merge upstream/development
  ```

## Install system dependencies

These are softwares on which our Open Event server depends, and C-based libraries on which our Python packages depend.

### For Mac OS

```sh
brew install postgresql
brew install python@3
brew install libmagic
brew install redis
```

**Note:** For Mac OS Sierra users, if you get an error that 'openssl/aes.h' could not be found when installing requirements.txt using pip, try the steps shown here - [OSX openssl header error](https://tutorials.technology/solved_errors/1-OSX-openssl_opensslv_h-file-not-found.html)

### For Debian/Ubuntu

Enter the project source folder and run:

```sh
xargs -a deb-packages.txt sudo apt install
```

In case you use Ubuntu 20.04+, where Python 3.7 is not provided in official repo, you can use [pyenv](https://github.com/pyenv/pyenv) to install Python 3.7 (Open Event Server is not compatible with Python 3.8+ yet).

## Create a Python virtual environment

Python virtual environment is a way to keep this project's collection of libraries not interfere with other projects or the system. There are many ways to create Python virtual environment (all have the same core), like:

- Use Python built-in tool:

  ```sh
  python3 -m venv my-project-name
  ```

- Use third-party tools:

  ```sh
  mkvirtualenv my-project-name -p /usr/bin/python3
  ```

I (Quân) recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) because:

- It gathers all virtual environments to one place. That let you know which virtual environments you created.
- It provides auto-complete command to enter a virtual env (`workon my-env`), list and delete them.
- It let you enter a virtual env no matter where you are standing.

Some tools, like Pipenv, puts virtual environment into your project code folder. That approach has some disadvantage:

- When you do somethings that involve scanning source code (like running test cases, search for file content), you accidentally scan the Python packages in the virtual environment.
- You don't know how many virtual environments you created.
- You have to know the path of an virtual environment in order to enter (if you are not standing in project folder).

After creating virtual environment, you should upgrade `pip`, `wheel` libraries inside it.

```sh
pip install -U pip wheel setuptools
```

## Install Python packages

- Activate the Python virtual environment you created for this project.
- Enter the project folder and run:

  ```sh
  pip3 install -r requirements.txt
  ```

After installing dependencies in your virtual environment, you need to configure pre-commit hooks by running the command

```sh
pre-commit install
```

## Create database

### For Linux users

The default database name used by Open Event server is `oevent` and `opev_test` for test cases.
To ease development, we should connect to PostgreSQL with the same username as Linux user, without creating password.

```sh
# Make yourself superuser in PostgeSQL
sudo -u postgres createuser -s $USER
# You are already a superuser, you can freely create new database
createdb oevent -O $USER
createdb opev_test -O $USER
```

This method is called "ident" method, where the connection is established via "Unix domain socket", which is a file, instead of a pair of IP:port. This method is safe because:

- No password to protect.
- Only available to same-machine clients, meaning no worries about attack from outside.

### For MAC users

(Not sure how to make it behave like Linux above - Quân)

```sh
psql -d postgres
```

Inside `psql`'s shell:

```sql
CREATE USER open_event_user WITH PASSWORD 'opev_pass';
CREATE DATABASE oevent WITH OWNER open_event_user;
CREATE DATABASE opev_test WITH OWNER open_event_user;
```

Once the databases are created, exit the psql shell with `\q` followed by ENTER.

## Generate configuration

```sh
cp .env.example .env
```

Add `SECRET_KEY={{something random}}` in .env file for cryptographic usage. Note that server will not run in production mode if you don't supply a secret.
To get a good secret value, run `python -c 'import secrets;print(secrets.token_hex())'` in a terminal and replace `{{something random}}` with its output in the line above and paste it in `.env` file.

If you created a dedicated PostgreSQL user and password, you should update the *.env* file content.

## Create database tables

Please run these inside Python virtual environment

```sh
python3 create_db.py
# enter email and password
python3 manage.py db stamp head
```

**Note:** In case you are using Anaconda distribution for python, you may get an import error regarding `celery.signals` module. Please use the default python version while executing these steps in that case.

## Start application

```sh
# For macOS
brew services start redis

# Run Celery
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
INTEGRATE_SOCKETIO=false celery worker -A app.instance.celery

# run app
python3 manage.py runserver
```

- Rejoice. Go to `localhost:5000` in your web browser to see the application live.

## Flask-SocketIO development

[Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) has been used in the project for displaying real-time notifications to the user. Although it's switched off by default. To integrate SocketIO you must set the `INTEGRATE_SOCKETIO` variable to `true` at bash.

```bash
export INTEGRATE_SOCKETIO="true"
```

The development server is the one that Flask ships with. It's based on Werkzeug and does not support WebSockets. If you try to run it, you'll get a RunTime error, something like: `You need to use the eventlet server. `. To test real-time notifications, you must use the Gunicorn web server with eventlet worker class.

If you've installed development requirements, you should have both `gunicorn` and `eventlet` installed. To run application on port 5000, execute the following instead of `python3 manage.py runserver`:

```bash
gunicorn app.instance:app --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload
```

`-w` specifies the number of worker classes to be used. `--reload` is used for development environments, so the server is restarted if any of the application python files change.

Now you should be able to access the website at `localhost:5000`.

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

---
