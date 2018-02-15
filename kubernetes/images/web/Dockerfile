FROM python:2-slim
MAINTAINER Niranjan Rajendran <niranjan94@yahoo.com>


ARG COMMIT_HASH
ARG BRANCH
ARG REPOSITORY

ENV COMMIT_HASH ${COMMIT_HASH:-null}
ENV BRANCH ${BRANCH:-master}
ENV REPOSITORY ${REPOSITORY:-https://github.com/fossasia/open-event-server.git}

# apt-get update
RUN apt-get clean -y && apt-get update -y
# update some packages
RUN apt-get install -y wget git ca-certificates curl && update-ca-certificates
# install deps
RUN apt-get install -y --no-install-recommends build-essential python-dev libpq-dev libevent-dev libmagic-dev

ENV INSTALL_PATH /opev

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .

RUN bash setup.sh

WORKDIR $INSTALL_PATH/open_event
