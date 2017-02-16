#! /bin/sh

set -e

echo "----- Updating Python Dependencies -----"
pip install -r requirements-dev.txt

echo "----- Updating Node Dependencies -----"
npm install

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Initializing Groups -----"
python manage.py initgroups
