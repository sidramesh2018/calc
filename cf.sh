#!/bin/bash

set -e

if [ $CF_INSTANCE_INDEX = "0" ]; then
    echo "----- Migrating Database -----"
    python manage.py migrate --noinput

    echo "----- Updating search field -----"
    python manage.py update_search_field

    echo "----- Initializing Groups -----"
    python manage.py initgroups

    echo "----- Downloading NLTK Data -----"

    if [ -d "${NLTK_DATA_DIR}" ]; then
      NLTK_OPTS="-d ${NLTK_DATA_DIR}"
    else
      NLTK_OPTS=""
    fi

    python -m nltk.downloader averaged_perceptron_tagger ${NLTK_OPTS}

fi
echo "------ Starting APP ------"
gunicorn calc.wsgi:application
