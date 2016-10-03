/* global window */

/**
 * This is just a wrapper around Google Analytics' ga() function, which
 * should be included inline at the top of the page. If it wasn't included
 * at the top of the page, however, we'll just provide a no-op function
 * so that code which calls it still works, allowing GA to be an optional
 * dependency.
 */

module.exports = typeof window.ga === 'function' ? window.ga : () => {};
