FROM python:3.11-alpine AS builder

LABEL maintainer="Chaojie Yan <ushareroses@gmail.com>"

# Setup basic Linux packages
RUN apk update && \
    apk add --no-cache tini tzdata build-base libffi-dev make && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

# Set workdir
WORKDIR /app/bili-jeans/

COPY . .

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.3 \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # no virtual env need for container
    POETRY_VIRTUALENVS_CREATE=false \
    # Add PYTHONPATH
    PYTHONPATH=/app/bili-jeans/

# install dependencies
RUN python -m pip install --no-cache --upgrade pip && \
    python -m pip install --no-cache poetry==${POETRY_VERSION} && \
    poetry install && \
    find /usr/local/ -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

FROM python:3.11-alpine AS dev

COPY --from=builder /etc/ /etc/
COPY --from=builder /usr/ /usr/
COPY --from=builder /app/bili-jeans/ /app/bili-jeans/
COPY --from=builder /sbin/ /sbin/

# Set workdir
WORKDIR /app/bili-jeans/

# Tini is now available at /sbin/tini
ENTRYPOINT ["/sbin/tini", "--"]
