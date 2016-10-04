# Browser tests via Selenium

To run CALC's browser-based tests via Selenium/WebDriver, you'll need to
define the following environment variables (unless otherwise noted):

* `DJANGO_LIVE_TEST_SERVER_ADDRESS` is the IP and port that CALC
  will bind itself to from the perspective of the machine (or
  Docker container) running the tests, e.g. `0.0.0.0:8000`.

* `WD_HUB_URL` is the URL at which the [Selenium hub][] server resides
  from the perspective of the machine (or Docker container) running
  the tests, e.g. `http://localhost:4444/wd/hub`.

* `WD_TESTING_URL` is the URL from which the automated browser will be able
  to access CALC, e.g. `http://localhost:8000`. (This will literally be
  the base URL that appears in the automated browser's address bar.)

* `WD_TESTING_BROWSER` is the browser used to perform the automated tests.
  Examples include `chrome`, `firefox`, `internet explorer`, `android`,
  `chrome`, `iPhone`, `iPad`, `opera`, and `safari`.

## Example: Docker + your machine's Chrome browser

If you're using Docker, configuration may not be straightforward due
to the fact that CALC is running in its own Docker container with its
own network.

Below is an example configuration for running tests in your
host machine's Chrome browser; they assume that you're using a native
version of Docker that exposes CALC through `localhost` at the
default `DOCKER_EXPOSED_PORT` of `8000`.

1. Download [Selenium Standalone Server][].  To run it, you will need to
   install Java too. Start it up with `java -jar` followed by the
   name of the `.jar` file you downloaded.

2. Download [ChromeDriver][], decompress its executable and put it in the
   same directory as Selenium Standalone Server.

3. Set the following environment variables in your `.env` file:

   ```
   DJANGO_LIVE_TEST_SERVER_ADDRESS=0.0.0.0:8000
   WD_TESTING_URL=http://127.0.0.1:8000
   WD_TESTING_BROWSER=chrome
   ```

   You will also want to define `WD_HUB_URL` in a way that allows your
   docker container to make a request to the Selenium server running on
   your machine.  One way to do this is by using the IP address of your
   machine on your LAN; on OS X, for instance, you should be able to
   use the output of the following command:

   ```
   echo "http://`ipconfig getifaddr en0`:4444/wd/hub"
   ```

   Supposing the above command produced the output
   `http://192.168.1.5:4444/wd/hub`, you can test connectivity from CALC's
   docker container by running:

   ```
   docker-compose run app curl -I http://192.168.1.5:4444/wd/hub
   ```

   This command should result in a 302 if it's able to connect to your
   Selenium server.

4. If you're running `docker-compose up` in a separate terminal,
   shut it down now, because the test server is going to be exposing
   itself on the same port as that development server.

5. Run the following:

   ```
   docker-compose run --service-ports app python manage.py test frontend
   ```

   If you need to run this multiple times but aren't changing any
   front-end code between runs, set `SKIP_STATIC_ASSET_BUILDING=yup` in
   your `.env` to make things run faster.


### Running Selenium and a headless Chrome browser in Docker

We can modify the earlier setup to use a [Selenium Docker image][] that
runs the Selenium hub server and a headless Chrome browser in a Docker
container.  The advantage is that you don't need to have Java, Selenium hub,
Chrome, and ChromeDriver on your local system; the downside is that you won't
be able to see what's happening except via screenshots taken by the test
suite.

In a separate terminal, run:

```
docker run -it --rm -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome:2.53.1
```

Your `WD_HUB_URL` should remain unchanged, since the same port on your
machine is hosting the Selenium server (it's just forwarding all requests to
the container now).

However, you will need to change the IP address of your `WD_TESTING_URL`,
as the browser is no longer running on your machine, but inside a Docker
container. You'll probably want to give it the same IP that `WD_HUB_URL`
uses.

[Selenium hub]: https://seleniumhq.github.io/docs/grid.html#what_is_a_hub_and_node
[Selenium Standalone Server]: http://www.seleniumhq.org/download/
[ChromeDriver]: https://sites.google.com/a/chromium.org/chromedriver/
[Selenium Docker image]: https://github.com/SeleniumHQ/docker-selenium
