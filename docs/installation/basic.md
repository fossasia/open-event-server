---
title: Generic
---

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


* **Step 3** - Install bower and frontend requirements.

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
python manage.py runserver
```

* **Step 8** - Rejoice. Go to `localhost:5000` in your web browser to see the application live.

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
