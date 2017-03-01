#! /bin/sh

set -e

echo "----- Updating Python Dependencies -----"
pip install -r requirements-dev.txt

echo "----- Updating Node Dependencies -----"
npm install

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Updating search field -----"
# The '-W ignore is to suppress https://github.com/18F/calc/issues/291.
python -W ignore manage.py update_search_field contracts

echo "----- Initializing Groups -----"
python manage.py initgroups
