/* global $ QUnit document */

import { IS_SUPPORTED, activate } from '../data-capture/smooth-scroll.js';

QUnit.module('smooth-scroll');

function test(name, cb) {
  if (!IS_SUPPORTED) {
    return QUnit.skip(name, cb);
  }

  return QUnit.test(name, cb);
}

// Ugh, some browsers don't fire `onhashchange` within iframes, so
// we'll polyfill it.
function addHashChangePolyfill(window) {
  let oldHash = window.location.hash;

  window.setInterval(() => {
    const newHash = window.location.hash;

    if (newHash !== oldHash) {
      $(window).trigger('hashchange');
      oldHash = newHash;
    }
  }, 10);
}

test('it works', assert => {
  const iframe = document.createElement('iframe');
  const getScrollTop = () =>
    $('body', iframe.contentDocument).scrollTop() ||
    $('html', iframe.contentDocument).scrollTop();

  $(iframe).appendTo('body').css({
    height: '50px',
    visibility: 'hidden',
  });

  iframe.contentDocument.open();
  iframe.contentDocument.write([
    '<a href="#foo">foo</a>',
    '<h1>hello</h1>',
    '<h2>there</h2>',
    '<h2 id="foo">foo</h1>',
  ].join('\n'));
  iframe.contentDocument.close();

  addHashChangePolyfill(iframe.contentWindow);

  const done = assert.async();
  const steps = (function* runSteps() {
    assert.equal(iframe.contentWindow.location.hash, '');
    assert.equal(getScrollTop(), 0);

    yield $('a', iframe.contentDocument).click();

    assert.equal(iframe.contentWindow.location.hash, '#foo');
    assert.ok(getScrollTop() !== 0);

    yield iframe.contentWindow.history.back();

    assert.equal(iframe.contentWindow.location.hash, '');
    assert.equal(getScrollTop(), 0);

    yield iframe.contentWindow.history.forward();

    assert.equal(iframe.contentWindow.location.hash, '#foo');
    assert.ok(getScrollTop() !== 0);

    $(iframe).remove();
    done();
  }());

  activate(iframe.contentWindow, {
    scrollMs: 50,
    onScroll: () => steps.next(),
  });

  steps.next();
});
