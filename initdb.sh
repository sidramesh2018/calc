#!/bin/bash
echo "------ Create database tables ------"
python manage.py migrate --noinput
python manage.py load_data
gunicorn hourglass.wsgi:application
