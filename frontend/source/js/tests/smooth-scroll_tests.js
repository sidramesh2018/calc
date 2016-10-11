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
  const done = assert.async();
  const iframe = document.createElement('iframe');
  const getScrollTop = () =>
    $('body', iframe.contentDocument).scrollTop() ||
    $('html', iframe.contentDocument).scrollTop();
  let step = 1;
  document.body.appendChild(iframe);

  $(iframe).css({
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

  activate(iframe.contentWindow, {
    scrollMs: 50,
    onScroll: () => {
      if (step === 1) {
        assert.equal(iframe.contentWindow.location.hash, '#foo');
        assert.ok(getScrollTop() !== 0);
        iframe.contentWindow.history.back();
      } else if (step === 2) {
        assert.equal(iframe.contentWindow.location.hash, '');
        assert.equal(getScrollTop(), 0);
        $(iframe).remove();
        done();
      } else {
        throw new Error(`unexpected step: ${step}`);
      }
      step++;
    },
  });

  assert.equal(iframe.contentWindow.location.hash, '');
  assert.equal(getScrollTop(), 0);
  $('a', iframe.contentDocument).click();
});
