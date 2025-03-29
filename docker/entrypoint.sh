#!/bin/sh
flask db upgrade

#python -m app.utils.load_defaults

gunicorn -b 0.0.0.0:5000 --timeout 120 --workers 5 --threads 2 run:app