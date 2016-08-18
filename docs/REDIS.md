# Redis

Orga Server requires Redis to run Celery which runs the background tasks in the application.

To setup Redis in your system, use the `run_redis.sh` script. It will download and build redis in the project's folder.
Also if Redis has been already downloaded, it won't download it again.

```sh
bash run_redis.sh
```

To start the redis server, run the following command while at project's root directory.

```sh
redis-3.2.1/src/redis-server
```

You can use ampersand (&) at the end of the above command if you want to start redis server as daemon (in background).

```sh
redis-3.2.1/src/redis-server &
```
