// @ts-check
/* eslint-env browser */

/**
 * This is DAP's weird exported Google Analytics function, documented
 * at:
 *
 *     https://github.com/digital-analytics-program/gov-wide-code
 *
 */
function gas(...args) {
  const origGas = window['gas'];         // eslint-disable-line dot-notation
  if (typeof origGas === 'function') {
    return origGas.apply(this, args);
  }
  return undefined;
}

/**
 * This is just a wrapper around Google Analytics' ga() function, which
 * should be included inline at the top of the page. If it wasn't included
 * at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing GA to be an optional
 * dependency.
 */

export default function ga(...args) {
  const origGa = window['ga'];         // eslint-disable-line dot-notation
  if (typeof origGa === 'function') {
    return origGa.apply(this, args);
  }
  return undefined;
}

/**
 * Track a "virtual pageview" using Google Analytics. Typically
 * used in single-page apps and such.
 *
 * @param {string} [url] The URL of the page to track, e.g. '/boop'.
 *   Defaults to the current page's URL, including the current
 *   search query.
 */
export function trackVirtualPageview(url) {
  ga('set', 'page', url || location.pathname + location.search);
  ga('send', 'pageview');
  gas('send', 'pageview', url);
}
