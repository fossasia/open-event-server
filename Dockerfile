FROM python:3.7.5-alpine as base

####

FROM base as builder

WORKDIR /install

RUN apk update && \
  apk add --virtual build-deps git gcc python3-dev musl-dev jpeg-dev zlib-dev libevent-dev file-dev libffi-dev openssl && \
  apk add postgresql-dev && \
  pip install setuptools

ADD requirements.txt /requirements.txt
ADD requirements /requirements/

ENV PYTHONPATH /install/lib/python3.7/site-packages
RUN LIBRARY_PATH=/lib:/usr/lib pip install --prefix=/install -r /requirements.txt

####

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add postgresql-dev ca-certificates libxslt jpeg zlib file libxml2 git

WORKDIR /data/app
ADD . .

EXPOSE 8080
CMD ["sh", "scripts/container_start.sh"]
