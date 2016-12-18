FROM python:2-slim
MAINTAINER Avi Aryan <avi.aryan123@gmail.com>

ENV INSTALL_PATH /open_event
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

# apt-get update and update some packages
RUN apt-get update && apt-get install -y wget git ca-certificates curl && update-ca-certificates && apt-get clean -y


# install deps
RUN apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev && apt-get clean -y && curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs && apt-get clean -y && npm install bower -g && npm cache clean
# nodejs bower
# ^^ https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions


# copy just requirements
COPY requirements.txt requirements.txt
COPY requirements requirements
COPY bower.json bower.json
COPY .bowerrc .bowerrc
COPY package.json package.json

# install requirements
RUN pip install --no-cache-dir -r requirements.txt && bower install --allow-root && bower cache clean --allow-root

# copy remaining files
COPY . .

CMD bash scripts/docker_run.sh
