# Docker

* Get the latest version of docker. See the [offical site](https://docs.docker.com/engine/installation/) for installation info for your platform.

* Install the latest version of docker-compose. Windows and Mac users should have docker-compose by default as it is part of Docker toolbox. For Linux users, see the
[official guide](https://docs.docker.com/compose/install/).

* Run `docker` and `docker-compose` in terminal to see if they are properly installed.

* Clone the project and cd into it.

```bash
git clone https://github.com/fossasia/open-event-server.git && cd open-event-server
```

* Then set the required `SERVER_NAME` environment variable. `SERVER_NAME` should the same as the domain on which the server is running and it should not include 'http', 'https',
'www' or the trailing slash (/) in the url. Examples - `domain.com`, `sub.domain.com`, `sub.domain.com:5000` etc

```bash
export SERVER_NAME=localhost;
```

* In the same terminal window, run `docker-compose build` to build open-event-server's docker image. This process can take some time.

* After build is done, run `docker-compose up` to start the server.

* If you are doing it for the first time, you will have to create the database (and then tables).
So keeping `docker-compose up` active in one terminal window, open another terminal window **in the same directory**. In there type the following command.

```bash
docker-compose run postgres psql -h postgres -p 5432 -U open_event_user --password open_event
```

* Write 'opev_pass' as password and ENTER. When inside psql shell, write the following command -

```sql
create database opev;
# CREATE DATABASE
```

* Then exit the shell by typing `\q` and ENTER.

* Now the database is created, so let's create the tables. Open the application's shell by `docker-compose run web sh`. Then write the following commands.

```bash
python3 create_db.py
# ^^ write super_admin email and password when asked
python3 manage.py db stamp head
```

* Close the application's shell by `exit` command.

* That's it. Go to `localhost` on the web browser and Open Event Orga Server will be live.


### Updating the Docker image

* To update the Docker image with a more recent version of open-event-server, you follow the same steps.

* `docker-compose build` followed by `docker-compose up`.

* Then open a new terminal window in same directory and run the following.

```bash
docker-compose run web python3 manage.py db upgrade
```

* That should be all. Open `localhost` in web browser to view the updated open-event-server.



#### Version information

This guide was last checked with docker version 1.12.0 and docker-compose version 1.8.0 on a Ubuntu 14.04 x64 system.
