/* global QUnit window */

import * as ga from '../common/ga';

function clearGa() {
  delete window.ga;
  delete window.gas;
}

QUnit.module('ga', {
  beforeEach: clearGa,
  afterEach: clearGa,
});

QUnit.test('ga does not throw when window.ga is undefined', (assert) => {
  ga.ga();
  assert.ok(true, 'calling ga() does not throw');
});

QUnit.test('ga calls window.ga when it is a function', (assert) => {
  window.ga = (...args) => {
    assert.deepEqual(args, [1, 2, 3]);
  };
  ga.ga(1, 2, 3);
});

QUnit.test('gas does not throw when window.gas is undefined', (assert) => {
  ga.gas();
  assert.ok(true, 'calling gas() does not throw');
});

QUnit.test('gas calls window.gas when it is a function', (assert) => {
  window.gas = (...args) => {
    assert.deepEqual(args, [1, 2, 3]);
  };
  ga.gas(1, 2, 3);
});

QUnit.test('trackVirtualPageview() works', (assert) => {
  const log = [];
  window.ga = (...args) => {
    log.push('ga', args);
  };
  window.gas = (...args) => {
    log.push('gas', args);
  };
  ga.trackVirtualPageview('/blah');
  assert.deepEqual(log, [
    "ga",
    [
      "set",
      "page",
      "/blah"
    ],
    "ga",
    [
      "send",
      "pageview"
    ],
    "gas",
    [
      "send",
      "pageview",
      "/blah"
    ]
  ]);
});

QUnit.test('trackEvent() does not throw', (assert) => {
  assert.expect(2);
  window.ga = window.gas = (...args) => {
    assert.deepEqual(args, [
      'send', 'event', 'funky-widget', 'click', 'someCategory'
    ]);
  };
  ga.trackEvent('funky-widget', 'click', 'someCategory');
});
