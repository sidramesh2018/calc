## Setup

CALC is primarily a [Django] project.

CALC uses [Docker][] and [Docker Compose][] to make setting up a development environment easier.

If you are unfamiliar with Docker or Docker Compose, read their docs as well as the [18F Docker guide][].

### Prerequisites

First, install [Docker](https://docs.docker.com/install/), as well as [Docker Compose](https://docs.docker.com/compose/install/) if it's not included in your system's Docker installation.

Check that both are installed by running:

```sh
docker -v
docker-compose -v
```

which will output the version numbers of each tool if the installation worked as expected.

### Configuration

```sh
cp .env.sample .env
ln -sf docker-compose.local.yml docker-compose.override.yml
```

Edit the `.env` file to your tastes. You shouldn't need to change much here; but if you'd like to see the available options, see [Environment variables](environment.md) for details on configuration.

### Installing or updating dependencies

Run

```sh
./docker-update.sh
```

This script will install/update all Python and Node dependencies, as well as apply any necessary database migrations.

You'll also want to run this script whenever you update your local repository via commands like `git pull` or `git checkout`.

### Loading data (optional)

You can optionally load some data into your dockerized database with:

```sh
docker-compose run app python manage.py load_api_data --end-page=5
```

This will load about 1000 rates from the production CALC instance into your local CALC instance.  You can increase the value passed to the `--end-page` argument to increase the amount of data that is copied over, or you can leave out the argument entirely to transfer all of CALC's data, but it may take some time.

### Starting the development server

Now you can start the development server:

```sh
docker-compose up
```

This will start up all required servers in containers and output their log information to `stdout`. It might take a couple minutes for all the front end assets to be built, but once you see a message that looks like

```sh
gulp_1          | [19:38:15] Finished 'default' after 23 μs
```

you can http://localhost:8000/ to see your local CALC instance.

### More information

For more information on interacting with CALC's dockerized development environment, see the [Docker section](docker.md) of our docs.

[Django]: https://www.djangoproject.com/
[18F Docker guide]: https://github.com/18F/development-guide/blob/master/project_setup/docker/README.md
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
[docker-machine-cloud]: https://docs.docker.com/machine/get-started-cloud/
