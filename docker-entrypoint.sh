#!/bin/sh
set -e
# Generate JWT keys at runtime if not already mounted (e.g. from Kubernetes secret)
if [ ! -f /app/keys/private.pem ] || [ ! -f /app/keys/public.pem ]; then
  echo "Generating JWT keys at runtime..."
  openssl genrsa -out /app/keys/private.pem 2048
  openssl rsa -in /app/keys/private.pem -pubout -out /app/keys/public.pem
fi
alembic upgrade head
exec "$@"
