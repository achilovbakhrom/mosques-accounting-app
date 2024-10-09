#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
poetry run python manage.py migrate &&
             poetry run python manage.py createsuperuser --no-input || true

# Collect static files
echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput

# Start the Gunicorn server
echo "Starting server..."
poetry run gunicorn mosques_app.wsgi:application --bind 0.0.0.0:8000
