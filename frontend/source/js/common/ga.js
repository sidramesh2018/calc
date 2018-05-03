// @ts-check
/* eslint-env browser */

/**
 * This is DAP's weird exported Google Analytics function, documented
 * at:
 *
 *     https://github.com/digital-analytics-program/gov-wide-code
 *
 * If DAP wasn't included at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing DAP to be an optional
 * dependency.
 */
export function gas(...args) {
  const origGas = window['gas'];
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
export function ga(...args) {
  const origGa = window['ga'];
  if (typeof origGa === 'function') {
    return origGa.apply(this, args);
  }
  return undefined;
}

/**
 * Track a "virtual pageview" using Google Analytics. Typically
 * used in single-page apps and such. For more details, see:
 * 
 *   https://developers.google.com/analytics/devguides/collection/analyticsjs/pages
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


/**
 * Track a custom event. For more details, see:
 * 
 *   https://developers.google.com/analytics/devguides/collection/analyticsjs/events
 *
 * @param {string} category The event category; typically the object that
 *   was interacted with, e.g. 'download-graph'.
 * @param {string} action The type of interaction, e.g. 'click'.
 * @param {string} [label] Optional label for the event, useful for
 *   categorization.
 */
export function trackEvent(category, action, label) {
  ga('send', 'event', category, action, label);
  gas('send', 'event', category, action, label);
}
