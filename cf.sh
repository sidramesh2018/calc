#!/bin/bash
if [ $CF_INSTANCE_INDEX = "0" ]; then
    echo "----- Migrating Database -----"
    python manage.py migrate --noinput
    echo "----- Initializing Groups -----"
    python manage.py initgroups
fi
echo "------ Starting APP ------"
newrelic-admin run-program gunicorn hourglass.wsgi:application
