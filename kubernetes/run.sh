#!/bin/bash
apt-get update
apt-get install -y wget git ca-certificates curl && update-ca-certificates && apt-get clean -y
apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev git && apt-get clean -y
curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs && apt-get clean -y
npm install bower -g && npm cache clean
pip install --no-cache-dir -r requirements.txt
bower install --allow-root && bower cache clean --allow-root
bash docker_run.sh
