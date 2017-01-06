# Running the Orga Server

This is a step-by-step guide on how to run orga-server in your computer.


## Dependencies required to run Orga Server

* Python 2
* Postgres
```sh
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```
* NodeJS  
if nvm(Node Version Manager)  is not installed:  
using cURL:
```sh
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.1/install.sh | bash
```
or Wget:
```sh
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.32.1/install.sh | bash
```
run nvm after exporting NVM_DIR:
```sh
. "$NVM_DIR/nvm.sh"
```
Node installation, v6.9.1 is LTS, though you can install other versions as well:
```sh
nvm install 6.9.1
```

## Steps

Make sure you have the dependencies mentioned above installed before proceeding further.

* **Step 1** - Install python requirements. You need to be present into the root directory of the project.

```sh
sudo -H pip install -r requirements.txt
```


* **Step 2** - Create the database. For that we first open the psql shell. Go the directory where your postgres file is stored.

```sh
sudo -u postgres psql
```

* When inside psql, create a user for open-event and then using the user create the database.

For ease development, you should create Postgres user with the same username as your OS account. If your OS login account is _john_, for example, you should create _john_ user in Postgres. By this, you can skip entering password when using database.

```sql
CREATE USER john WITH PASSWORD 'start';
CREATE DATABASE oevent WITH OWNER john;
```

* Once database is created, exit the psql shell with `\q` followed by ENTER.


* **Step 3** - Install bower and frontend requirements. Learn more at [BOWER.md](../README.md#how-to-configure-bower). For this you need to be present in the root directory of the project. The root directory contains the file ```bower.json```. When you write ```bower install```, it finds bower.json and installs the libraries on the system.

```sh
npm install bower -g
bower install
```
for mac user:
```sh
sudo npm install bower -g
bower install
```

* **Step 4** - Create application environment variables.

```sh
export DATABASE_URL=postgresql:///oevent
export SERVER_NAME=localhost:5000
```

The URL is short, thank to the resemble of Postgres user and OS user.


* **Step 5** - Start the postgres service.

```sh
sudo service postgresql restart
```
for mac users:

```sh
brew services restart postgresql
```

* **Step 6** - Create the tables. For that we will use `create_db.py`.

```sh
python create_db.py
# enter email and password
python manage.py db stamp head
```


* **Step 7** - Start the application along with the needed services.

```sh
# Install and run redis
# For Ubuntu, Debian and alike
sudo apt install redis-server
# For Fedora, RedHat, CentOS
sudo dnf install redis-server

# Run Celery
# socketio has problems with celery "blocking" tasks
# also socketio is not used in a celery task so no problem to turn it off
INTEGRATE_SOCKETIO=false celery worker -A app.celery

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
sudo service nginx testconfig # Should respond with "test is successful"
sudo service nginx restart
gunicorn app:app --worker-class eventlet -w 1 --bind 0.0.0.0:5001 --reload
```

---

**Note:**

If you are working from within a proxied network of an organization/institute, Bower might not be able to install the libraries. For that, we need to configure .bowerrc to work via proxy.
* Open .bowerrc in any text editor like vim. Run:
```vim .bowerrc```
* The contents of .bowerrc will be something like this:
```
{
	"directory": "app/static/admin/lib"
}
```
* Modify the file to add "proxy" and "https-proxy" properties like this:
```
{
	"directory": "app/static/admin/lib",
	"proxy": "http://172.31.1.23:8080",
	"https-proxy": "http://172.31.1.23:8080"
}
```
