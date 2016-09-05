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
create user open_event_user with password 'start';
create database test with owner=open_event_user;
```

* Once database is created, exit the psql shell with `\q` followed by ENTER.


* **Step 3** - Install bower and frontend requirements. Learn more at [BOWER.md](../README.md#how-to-configure-bower)

```sh
npm install bower -g
bower install
```


* **Step 4** - Create application environment variables.

```sh
export DATABASE_URL=postgresql://open_event_user:start@127.0.0.1:5432/test
export SERVER_NAME=localhost:5000
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
The `&` at the end of the commands below make them run in background so that they don't hold the terminal. See [REDIS.md](../README.md#redis) for more info.

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


## Flask-SocketIO development

[Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) has been used in the project for displaying real-time notifications to the user. Although it's switched off by default. To integrate SocketIO you must set the `INTEGRATE_SOCKETIO` variable to `true` at bash.

```bash
export INTEGRATE_SOCKETIO="true"
```

The development server is the one that Flask ships with. It's based on Werkzeug and does not support WebSockets. If you try to run it, you'll get a RunTime error, something like: `You need to use the eventlet server. `.  To test real-time notifications, you must use the Gunicorn web server with eventlet worker class.

If you've installed development requirements, you should have both `gunicorn` and `eventlet` installed. To run application on port 5000, execute the following instead of `python manage.py runserver`:

```bash
gunicorn app:app --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload
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
sudo ngnix -t # Should respond with "test is successful"
sudo service nginx restart
gunicorn app:app --worker-class eventlet -w 1 --bind 0.0.0.0:5001 --reload
```
