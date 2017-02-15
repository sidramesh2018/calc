#! /bin/sh

set -e

echo "----- Updating Python Dependencies -----"
pip install -r requirements-dev.txt

echo "----- Downloading NLTK Data -----"

if [ -d "${NLTK_DATA_DIR}" ]; then
  NLTK_OPTS="-d ${NLTK_DATA_DIR}"
else
  NLTK_OPTS=""
fi

python -m nltk.downloader averaged_perceptron_tagger ${NLTK_OPTS}

echo "----- Updating Node Dependencies -----"
npm install

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Initializing Groups -----"
python manage.py initgroups
