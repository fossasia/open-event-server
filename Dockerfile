FROM python:3.7-alpine as base

####

FROM base as builder

WORKDIR /install

RUN apk update && \
  apk add --virtual build-deps git gcc python3-dev musl-dev jpeg-dev zlib-dev libevent-dev file-dev libffi-dev openssl && \
  apk add postgresql-dev
# PDF Generation: weasyprint (libffi-dev jpeg-dev already included above)
RUN apk add --virtual gdk-pixbuf-dev

ADD requirements.txt /requirements.txt
ADD requirements /requirements/

RUN pip install --prefix=/install --no-warn-script-location -r /requirements.txt

####

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add postgresql-libs ca-certificates libxslt jpeg zlib file libxml2
# PDF Generation: weasyprint
RUN apk --no-cache add cairo-dev pango-dev ttf-opensans
RUN fc-cache -f

WORKDIR /data/app
ADD . .
RUN ["sh", "scripts/l10n.sh", "generate"]

EXPOSE 8080
ENTRYPOINT ["sh", "scripts/container_start.sh"]
