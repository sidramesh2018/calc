#!/bin/bash

# DEPLOY_ENV must be set to "dev", "staging", or "prod"

# CF_DEV_USER, CF_STAGING_USER, CF_PROD_USER, and the associated
# CF_DEV_PASSWORD, CF_STAGING_PASSWORD, and CF_PROD_PASSWORD
# are defined as private Environment Variables
# in the Travis web UI: https://travis-ci.org/18F/calc/settings

set -e

if [[ "$DEPLOY_ENV" = "dev" ]]; then
  DEPLOY_USER="$CF_DEV_USER"
  DEPLOY_PASS="$CF_DEV_PASSWORD"
elif [[ "$DEPLOY_ENV" = "staging" ]]; then
  DEPLOY_USER="$CF_STAGING_USER"
  DEPLOY_PASS="$CF_STAGING_PASSWORD"
elif [[ "$DEPLOY_ENV" = "prod" ]]; then
  DEPLOY_USER="$CF_PROD_USER"
  DEPLOY_PASS="$CF_PROD_PASSWORD"
else
  echo "Unrecognized or missing DEPLOY_ENV. Exiting."
  exit 1
fi

API="https://api.fr.cloud.gov"
ORG="fas-calc"

SPACE="$DEPLOY_ENV"
APP_NAME="calc-$DEPLOY_ENV"
MANIFEST="manifests/manifest-$DEPLOY_ENV.yml"

echo "Deploying to $DEPLOY_ENV space."

cf login -a $API -u $DEPLOY_USER -p $DEPLOY_PASS -o $ORG -s $SPACE
cf zero-downtime-push $APP_NAME -f $MANIFEST
