#!/bin/bash
# This script downloads and runs redis-server.
# If redis has been already downloaded, it just runs it
if [ ! -d redis-3.2.1/src ]; then
    wget http://download.redis.io/releases/redis-3.2.1.tar.gz
    tar xzf redis-3.2.1.tar.gz
    rm redis-3.2.1.tar.gz
    cd redis-3.2.1
    make
else
    cd redis-3.2.1
fi
src/redis-server
