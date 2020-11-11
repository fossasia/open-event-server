# Docker

* Get the latest version of docker. See the [official site](https://docs.docker.com/engine/installation/) for installation info for your platform.

* Install the latest version of docker-compose. Windows and Mac users should have docker-compose by default as it is part of Docker toolbox. For Linux users, see the
[official guide](https://docs.docker.com/compose/install/).

* Run `docker` and `docker-compose` in terminal to see if they are properly installed.

* Clone the project and cd into it.

```bash
git clone https://github.com/fossasia/open-event-server.git && cd open-event-server
```

* create env file using the following command

```sh
  cp .env.example .env
```
Add  SECRET_KEY in the env file to run properly in production mode . To generate a good secret value run python -c 'import secrets;print(secrets.token_hex())'
  
* In the same terminal window, run `docker-compose build` to build open-event-server's docker image. This process can take some time.

* After build is done, run `docker-compose up -d` to start the server.

* That's it. Go to `localhost:8080` on the web browser and Open Event Orga Server will be live.


### Installing open-event-frontend

* For installing the frontend using docker-compose, follow these [steps](https://github.com/fossasia/open-event-frontend/blob/development/docs/installation/docker.md).

* Change the API host in the *.env* file of the **frontend** to `localhost:8080`.


### Updating the Docker image

* To update the Docker image with a more recent version of open-event-server, you follow the same steps.

* `docker-compose build` followed by `docker-compose up`.

* Then open a new terminal window in same directory and run the following.

```bash
docker-compose run web python3 manage.py db upgrade
```

* That should be all. Open `localhost:8080` in web browser to view the updated open-event-server.



#### Version information

This guide was last checked with docker version 1.12.0 and docker-compose version 1.8.0 on a Ubuntu 14.04 x64 system.
