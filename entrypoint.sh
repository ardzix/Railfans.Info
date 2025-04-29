#!/bin/bash

# Wait for the database to be ready (if using PostgreSQL)
if [ "$USE_POSTGRES" = "true" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start supervisord
exec "$@" 