#! /bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <instance-name>"
  echo
  echo "This will spin up a new remote machine called <instance-name> and "
  echo "deploy CALC to it."
  exit 1
fi

export INSTANCE_NAME=$1
export ENV_FILE=activate-${INSTANCE_NAME}
export YML_FILE=docker-compose.${INSTANCE_NAME}.yml
export DOCKERFILE_FILE=Dockerfile.${INSTANCE_NAME}

echo "Provisioning Docker machine."

docker-machine create ${INSTANCE_NAME} \
  --driver=amazonec2 --amazonec2-instance-type=t2.large

echo "Creating ${DOCKERFILE_FILE}."

cat Dockerfile Dockerfile.cloud-extras > ${DOCKERFILE_FILE}

echo "Creating ${YML_FILE}."

cat << EOF > ${YML_FILE}
version: '2'
services:
  app:
    build:
      dockerfile: ${DOCKERFILE_FILE}
    environment:
      - DEBUG=yup
  rq_worker:
    build:
      dockerfile: ${DOCKERFILE_FILE}
    environment:
      - DEBUG=yup
  rq_scheduler:
    build:
      dockerfile: ${DOCKERFILE_FILE}
    environment:
      - DEBUG=yup
EOF

echo "Creating ${ENV_FILE}."

cat << EOF > ${ENV_FILE}
eval \$(docker-machine env ${INSTANCE_NAME})
export COMPOSE_FILE=docker-compose.yml:${YML_FILE}
export DOCKER_EXPOSED_PORT=80
export DOCKER_HOST_IP=\$(echo \${DOCKER_HOST} | sed 's/tcp:\/\/\([0-9.]*\).*/\1/')
echo "Now using Docker machine ${INSTANCE_NAME} at \${DOCKER_HOST_IP}."
EOF

source ${ENV_FILE}

docker-compose build

docker-compose pull

docker-compose run app python manage.py migrate

docker-compose run app python manage.py initgroups

docker-compose run app python manage.py load_data

docker-compose run app python manage.py load_s70

docker-compose up -d

echo "Your new instance of CALC is up at http://${DOCKER_HOST_IP}."
echo
echo "To target the remote machine's environment, run:"
echo
echo "  source ${ENV_FILE}"
echo
echo "Then any docker commands will be run on ${INSTANCE_NAME}."
