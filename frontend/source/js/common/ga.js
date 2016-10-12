/* global window */

/**
 * This is just a wrapper around Google Analytics' ga() function, which
 * should be included inline at the top of the page. If it wasn't included
 * at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing GA to be an optional
 * dependency.
 */

function ga(...args) {
  if (typeof window.ga === 'function') {
    return window.ga.apply(this, args);
  }
  return undefined;
}

module.exports = ga;

/**
 * Here we tell DAP to re-initialize auto tracking of links
 * whenever links are added to the page. For more background, see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/47
 */

function isAnchorInNodeList(list) {
  for (let i = 0; i < list.length; i++) {
    const node = list[i];

    if (node.nodeType === node.ELEMENT_NODE) {
      if (node.nodeName === 'a' || node.querySelector('a')) {
        return true;
      }
    }
  }
  return false;
}

if ('MutationObserver' in window) {
  const observer = new window.MutationObserver(mutations => {
    const wasAnchorAdded = mutations.some(
      mut => isAnchorInNodeList(mut.addedNodes)
    );
    if (wasAnchorAdded) {
      /* eslint-disable */
      const initAutoTracker = window._initAutoTracker;
      /* eslint-enable */

      if (typeof initAutoTracker === 'function') {
        initAutoTracker();
      }
    }
  });

  observer.observe(window.document.documentElement, {
    childList: true,
    subtree: true,
  });
}
