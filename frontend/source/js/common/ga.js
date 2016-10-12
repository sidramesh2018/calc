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
 * Here we notify DAP about new links we've added to the page, so that
 * it can auto-track them. For more background, see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/47
 */

function findLinksInNodeList(list) {
  const links = [];

  for (let i = 0; i < list.length; i++) {
    const node = list[i];

    if (node.nodeType === node.ELEMENT_NODE) {
      if (node.nodeName === 'a') {
        links.push(node);
      } else {
        const innerLinks = node.querySelectorAll('a');
        for (let j = 0; j < innerLinks.length; j++) {
          links.push(innerLinks[i]);
        }
      }
    }
  }

  return links;
}

/**
 * Well, this is horrible.
 *
 * To work around DAP's `_initAutoTracker()` getting *all* the links on
 * a page and adding event handlers to them--which is a problem because
 * it can lead to the same link being tracked multiple times--we will
 * temporarily "hack" the underlying DOM API being used to only give the
 * auto tracker the links we know aren't currently being tracked.
 *
 * For more details on a hopefully better workaround in the future,
 * see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/48
 */

function hackilyNotifyAutoTrackerOfNewLinks(initAutoTracker, links) {
  const oldGet = window.document.getElementsByTagName;

  window.document.getElementsByTagName = () => links;

  try {
    initAutoTracker();
  } finally {
    window.document.getElementsByTagName = oldGet;
  }
}

if ('MutationObserver' in window) {
  const observer = new window.MutationObserver(mutations => {
    /* eslint-disable */
    const initAutoTracker = window._initAutoTracker;
    /* eslint-enable */

    if (window.document.readyState === 'loading' ||
        typeof initAutoTracker !== 'function') {
      // DAP hasn't been loaded or initialized the auto tracker yet.
      // Once that happens, it'll find any links that were added as a
      // result of these particular mutations, so we can just leave now.
      return;
    }

    const links = mutations
      .map(mut => findLinksInNodeList(mut.addedNodes))
      .reduce((a, b) => a.concat(b), []);

    if (links.length) {
      hackilyNotifyAutoTrackerOfNewLinks(initAutoTracker, links);
    }
  });

  observer.observe(window.document.documentElement, {
    childList: true,
    subtree: true,
  });
}
