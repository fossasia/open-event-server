#!/bin/sh
docker run -d -e POSTGRES_PASSWORD=test -e POSTGRES_USER=test \
       --mount type=tmpfs,destination=/var/lib/postgresql/data \
       --rm -p 5433:5432 --name opev-test-db postgis/postgis:12-3.0-alpine
