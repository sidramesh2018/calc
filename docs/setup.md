## Setup

To install the requirements, use:

```sh
pip install -r requirements-dev.txt
npm install
```

CALC is a [Django] project. You can configure everything by running:

```sh
cp .env.sample .env
```

Edit the `.env` file to contain your local database configuration. Note
that you need to use postgres as a backend, since CALC uses its full-text
search functionality.

You'll also want to make sure you have a local instance of redis running,
on its default port, as we use it for CALC's task queue.

For guidance on installing Redis, see [Installing Redis on Mac OSX][redis-osx]
or [Installing Redis on Ubuntu][redis-ubuntu].

Assuming you have Postgres installed you can create the database:

```sh
createdb hourglass
```

Now run:

```sh
./manage.py syncdb
./manage.py initgroups
```

to set up the database. After that, you can load all of the data by running:

```sh
./manage.py load_data
./manage.py load_s70
```

From there, you're just a hop, skip and a jump away from your own dev server:

```sh
./manage.py runserver
```

In another terminal, you will also need to run `gulp` to watch and rebuild 
static assets. All the static assets (SASS for CSS and ES6 JavaScript) are 
located in the [frontend/source/](../frontend/source/) directory. Outputs
from the gulp build are placed in `frontend/static/frontend/built/`.
Examine [gulpfile.js](../gulpfile.js) for details of our gulp asset pipeline.

Note that if you are using our [Docker setup](docker.md), running gulp will
be handled for you.

```sh
npm run gulp
```

If you just want to build the assets once without watching for changes, run

```sh
npm run gulp -- build
```

Also, in yet another terminal, you will want to run
`python manage.py rqworker` to process all the tasks in the task queue.

[redis-ubuntu]: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04

[redis-osx]: https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298#.fa2s6i1my

[Django]: https://www.djangoproject.com/
