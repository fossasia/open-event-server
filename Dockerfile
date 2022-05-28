FROM python:3.8.6-alpine as base

####

FROM base as builder

RUN apk update && \
  apk add --virtual build-deps make git g++ python3-dev musl-dev jpeg-dev zlib-dev libevent-dev file-dev libffi-dev openssl && \
  apk add postgresql-dev libxml2-dev libxslt-dev
# PDF Generation: weasyprint (libffi-dev jpeg-dev already included above)
RUN apk add --virtual gdk-pixbuf-dev

ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN set -eo pipefail; wget -O - https://install.python-poetry.org | python -

WORKDIR /opt/pysetup

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root --no-dev

####

FROM base

COPY --from=builder /opt/pysetup/.venv /opt/pysetup/.venv

ENV PATH="/opt/pysetup/.venv/bin:$PATH"

RUN apk --no-cache add postgresql-libs ca-certificates libxslt jpeg zlib file libxml2
# PDF Generation: weasyprint
RUN apk --no-cache add cairo-dev pango-dev ttf-opensans
RUN fc-cache -f

WORKDIR /data/app
ADD . .
RUN ["sh", "scripts/l10n.sh", "generate"]

EXPOSE 8080
ENTRYPOINT ["sh", "scripts/container_start.sh"]
