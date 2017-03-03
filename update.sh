#! /bin/sh

set -e

echo "----- Updating Python Dependencies -----"
pip install -r requirements-dev.txt

echo "----- Updating Node Dependencies -----"
yarn

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Initializing Groups -----"
python manage.py initgroups

if [ -n "${CALC_IS_ON_DOCKER_IN_CLOUD}" ]; then
  echo "----- Building Static Assets -----"
  gulp build
fi
