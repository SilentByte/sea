#!/usr/bin/env bash

set -Eeuo pipefail
set -m

echo "Collecting static files..."
./sea.sh django collectstatic --no-input
cp -r /sea_server/public/static /public/static

echo "Migrating database models..."
./sea.sh django migrate

ADMIN_USER_NAME="${ADMIN_USER_NAME:-}"
ADMIN_USER_EMAIL="${ADMIN_USER_EMAIL:-}"
ADMIN_USER_PASSWORD="${ADMIN_USER_PASSWORD:-}"

if [[ ! -z "$ADMIN_USER_NAME" ]] && [[ ! -z "$ADMIN_USER_EMAIL" ]] && [[ ! -z "$ADMIN_USER_PASSWORD" ]]
then
    ./sea.sh django createadminuser \
      || echo "Failed to create admin user"
else
    echo "Skipping admin user creation..."
fi

echo "Synchronizing documents..."
./sea.sh django syncdocuments

echo "System is running, starting bringing Supervisor..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
fg %1
