#!/usr/bin/env bash

set -e

TIMESTAMP="$(date +'%Y%m%d%H%M%S')"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
COMMAND=$1

PYTHON=python

if [[ -e ./venv ]]; then
    PYTHON=./venv/bin/python
fi

command_help() {
    cat <<USAGE
  Usage: fts <command> [options]

  Commands:
    django                  Execute a Django Management Command
    dev-docker              Build & Run the system in a Docker container

USAGE
}

command_django() {
    ${PYTHON} sea_server/manage.py $@
}

command_dev_docker() {
  mkdir -p documents/

  docker build -t sea .
  docker run -it \
    -p 80:80 \
    --network host \
    --memory=1G \
    --memory-swap=1G \
    --env-file .env \
    -e DEBUG=False \
    -e DOCUMENT=/documents \
    -v "$PWD/documents":/documents:ro \
    sea:latest
}

case "$COMMAND" in
    "django") shift && command_django "$@" ;;
    "dev-docker") command_dev_docker ;;
    *) command_help ;;
esac
