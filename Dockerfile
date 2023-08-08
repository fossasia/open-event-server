FROM python:3.8.17-alpine as base

####

FROM base as builder

RUN apk update && \
  apk add --virtual build-deps make git g++ python3-dev musl-dev jpeg-dev zlib-dev libevent-dev file-dev libffi-dev openssl && \
  apk add postgresql-dev libxml2-dev libxslt-dev
RUN apk add fontconfig
RUN echo @edge http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories 
RUN apk add wqy-zenhei@edge


# PDF Generation: weasyprint (libffi-dev jpeg-dev already included above)
RUN apk add --virtual gdk-pixbuf-dev

RUN apk --no-cache add postgresql-libs ca-certificates libxslt jpeg zlib file libxml2
# PDF Generation: weasyprint
RUN apk --no-cache add cairo-dev pango-dev ttf-opensans

# Note: The custom PyPI repo is for AlpineOS only, where Python packages are compiled with musl libc. Don't use it on glibc Linux.
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_EXTRA_INDEX_URL=https://pypi.fury.io/fossasia/

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN set -eo pipefail; wget -O - https://install.python-poetry.org | python -

WORKDIR /opt/pysetup

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes --only main | poetry run pip install -r /dev/stdin

####

FROM base

# these libs are necessary for operation
RUN apk --no-cache add libmagic cairo pango ttf-opensans && \
    apk --no-cache add postgresql-libs libxslt jpeg zlib libxml2 # those *might* be useful
RUN apk --no-cache add fontconfig
RUN echo @edge http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories 
RUN apk --no-cache add wqy-zenhei@edge
RUN fc-cache -f

COPY --from=builder /opt/pysetup/.venv /opt/pysetup/.venv

ENV PATH="/opt/pysetup/.venv/bin:$PATH"

WORKDIR /data/app
ADD . .
RUN ["sh", "scripts/l10n.sh", "generate"]

EXPOSE 8080
ENTRYPOINT ["sh", "scripts/container_start.sh"]
