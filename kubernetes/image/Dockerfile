FROM python:2-slim
MAINTAINER Niranjan Rajendran <niranjan94@yahoo.com>

# apt-get update
RUN apt-get clean -y && apt-get update -y
# update some packages
RUN apt-get install -y wget git ca-certificates curl && update-ca-certificates
# install deps
RUN apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev
# nodejs bower
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs

ENV INSTALL_PATH /opev

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

RUN npm install bower -g && npm cache clean

COPY setup.sh setup.sh
