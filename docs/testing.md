## Testing

CALC provides a custom Django management command to run all linters and tests:

```sh
python manage.py ultratest
```

### Python unit tests

To run just unit tests:

```sh
py.test
```

For more information on running only specific tests, see
[`py.test` Usage and Invocations][pytest].

### Front end tests

For more details on front end testing, see the [front end guide](frontend.md).

### Using real-world browsers

By default, CALC's browser-based tests will run via PhantomJS. This
is nice because it requires no configuration (aside from installing
PhantomJS, if you're not using the Docker setup).

However, it might also be preferable to run the browser-based tests in
a real-world browser. This can be done via Selenium/WebDriver. The
trade-off is that this requires configuration.

For details on how to do this, see our in-depth [Selenium guide](selenium.md).

### Security scans

We use [bandit](https://github.com/openstack/bandit) for security-related
static analysis.

To run bandit:

```sh
bandit -r .
```

bandit's configuration is in the [`.bandit`](../.bandit) file.

[pytest]: https://pytest.org/latest/usage.html
