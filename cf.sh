#!/bin/bash
echo "------ Starting APP ------"
if [ $CF_INSTANCE_INDEX = "0" ]; then
    echo "----- Migrating Database -----"
    python manage.py migrate --noinput
    python manage.py initgroups
    echo "----- Loading Sample Labor Category Data -----"
    python manage.py load_data -f contracts/docs/hourly_prices_sample.csv
    python manage.py load_s70 -f contracts/docs/s70/s70_data_sample.csv
fi
newrelic-admin run-program gunicorn hourglass.wsgi:application
