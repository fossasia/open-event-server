#!/bin/bash
# This script downloads and installs redis-server.
# If redis has been already installed, it skips it
if [ ! -d redis-3.2.1/src ]; then
    wget http://download.redis.io/releases/redis-3.2.1.tar.gz
    tar xzf redis-3.2.1.tar.gz
    rm redis-3.2.1.tar.gz
    cd redis-3.2.1
    make
fi
