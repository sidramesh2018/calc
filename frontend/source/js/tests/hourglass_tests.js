const hourglass = require('../common/hourglass');

/* eslint-disable */
var test = QUnit.test,
    module = QUnit.module;

module("hourglass.API");

test("API()", function(assert) {
  assert.equal(new hourglass.API("/").path, "/", "sets the path properly");
});

test("#url()", function(assert) {
  var api = new hourglass.API("/api/");
  assert.equal(api.url("foo"), "/api/foo", "appends a URI to the path");
  assert.equal(api.url("/foo"), "/api/foo", "strips out superfluous path delimiters");
});

// test node-style callbacks
test("#get()", function(assert) {
  var api = new hourglass.API();

  var done1 = assert.async();
  api.get("rates", function(error, data) {
    if (error) throw error.statusText;
    assert.ok(data, "got data from rates endpoint");
    done1();
  });

  var done2 = assert.async();
  api.get("should-not-exist", function(error, data) {
    assert.ok(error, "got error for non-existent URI");
    done2();
  });

  var done3 = assert.async();
  api.get({uri: "rates", data: {q: "engineer"}}, function(error, data) {
    if (error) throw error.statusText;
    assert.ok(data, "got data from rates endpoint with data");
    done3();
  });
});
/* eslint-enable */
