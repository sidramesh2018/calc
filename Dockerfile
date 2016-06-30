FROM python:3.4

ENV PHANTOMJS_VERSION 1.9.7

# https://hub.docker.com/r/cmfatih/phantomjs/~/dockerfile/
RUN \
  mkdir -p /srv/var && \
  wget -q --no-check-certificate -O /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
  tar -xjf /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 -C /tmp && \
  rm -f /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
  mv /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/ /srv/var/phantomjs && \
  ln -s /srv/var/phantomjs/bin/phantomjs /usr/bin/phantomjs

RUN apt-get update && \
  apt-get install -y ruby-full rubygems && \
  gem install sass

COPY requirements.txt /calc/

RUN pip install -r /calc/requirements.txt

ENV DDM_IS_RUNNING_IN_DOCKER yup
ENV PYTHONUNBUFFERED yup

# The following lines set up our container for being run in a
# cloud environment, where folder sharing is disabled. They're
# irrelevant for a local development environment, where the /calc
# directory will be superseded by a folder share.

COPY . /calc/
WORKDIR /calc
RUN python manage.py collectstatic --noinput
