#!/bin/sh

echo "Waiting for MySQL..."
echo "⏳ Waiting for $DB_HOST:$DB_PORT..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done

echo "MySQL is up - continuing!"

flask db upgrade

python -m app.utils.load_defaults

gunicorn -b 0.0.0.0:5000 --timeout 120 --workers 5 --threads 2 run:app