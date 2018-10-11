FROM python:3.6-alpine as base
LABEL maintainer="Niranjan Rajendran <me@niranjan.io>"

##
##

FROM base as builder

WORKDIR /install

RUN apk update && \
  apk add --virtual build-deps git gcc python3-dev musl-dev jpeg-dev zlib-dev libevent-dev file-dev libffi-dev openssl && \
  apk add postgresql-dev && \
  pip install setuptools

ADD requirements.txt /requirements.txt
ADD requirements /requirements/

RUN wget https://bootstrap.pypa.io/ez_setup.py && python ez_setup.py

ENV PYTHONPATH /install/lib/python3.6/site-packages
RUN pip install --install-option="--prefix=/install" setuptools && \
    LIBRARY_PATH=/lib:/usr/lib pip install --install-option="--prefix=/install" -r /requirements.txt


##
##

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add postgresql-dev ca-certificates libxslt jpeg zlib file libxml2 git && \
    pip install git+https://github.com/fossasia/flask-rest-jsonapi.git@shubhamp-master#egg=flask-rest-jsonapi

WORKDIR /data/app
ADD . .

EXPOSE 8080
CMD ["sh", "scripts/container_start.sh"]
