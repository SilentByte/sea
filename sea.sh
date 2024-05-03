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

USAGE
}

command_django() {
    ${PYTHON} sea_server/manage.py "${@:1}"
}

case "$COMMAND" in
    "django") command_django "$2" ;;
    *) command_help ;;
esac
