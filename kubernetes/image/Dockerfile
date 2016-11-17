FROM python:2-slim
MAINTAINER Niranjan Rajendran <niranjan94@yahoo.com>

ENV REPOSITORY https://github.com/fossasia/open-event-orga-server.git
ENV BRANCH development

ARG COMMIT_HASH

# apt-get update
RUN apt-get clean -y && apt-get update -y
# update some packages
RUN apt-get install -y wget git ca-certificates curl && update-ca-certificates
# install deps
RUN apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev
# nodejs bower
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash && apt-get install -y --force-yes nodejs

RUN npm install bower -g && npm cache clean

ENV INSTALL_PATH /opev

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .

RUN bash setup.sh

WORKDIR $INSTALL_PATH/open_event
