#!/bin/sh
set -e

echo "→ Running database migrations..."
python manage.py migrate --noinput

echo "→ Collecting static files..."
python manage.py collectstatic --noinput

echo "→ Seeding demo catalog..."
python manage.py seed_catalog

echo "→ Creating roles..."
python manage.py create_roles

echo "→ Creating demo admin..."
python manage.py create_demo_admin

echo "→ Starting server..."
exec "$@"
