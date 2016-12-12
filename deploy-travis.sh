set -e

API="https://api.fr.cloud.gov"
ORG="fas-calc"
SPACE="dev"
APP_NAME="calc-dev"
MANIFEST="manifests/manifest-dev.yml"

# CF_DEV_USER and CF_DEV_PASSWORD are defined as private Environment Variables
# in the Travis web UI: https://travis-ci.org/18F/calc/settings
cf login -a $API -u $CF_DEV_USER -p $CF_DEV_PASSWORD -o $ORG -s $SPACE
cf zero-downtime-push $APP_NAME -f $MANIFEST
