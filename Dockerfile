FROM python:2-slim
MAINTAINER Avi Aryan <avi.aryan123@gmail.com>

ENV INSTALL_PATH /open_event
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

# apt-get update
RUN apt-get update
# update some packages
RUN apt-get install -y wget git ca-certificates curl && update-ca-certificates && apt-get clean -y
# install deps
RUN apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev && apt-get clean -y
# nodejs bower
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs && apt-get clean -y
# ^^ https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions
RUN npm install bower -g && npm cache clean

# copy just requirements
COPY requirements.txt requirements.txt
COPY requirements requirements
COPY bower.json bower.json
COPY package.json package.json

# install requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN bower install --allow-root && bower cache clean --allow-root

# copy remaining files
COPY . .

CMD bash docker_run.sh
