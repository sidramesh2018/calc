/* global $, document, window */

/**
 * This script alters the behavior of in-page linking to smoothly
 * scroll the user's browser. It preserves sequential focus navigation
 * to ensure that keyboard users aren't stranded.
 *
 * Implementation notes
 * --------------------
 *
 * We use `history.replaceState()` to remember the current scroll
 * position of the page, so that we can restore it when the user
 * presses their browser's back and forward buttons.
 *
 * When the user clicks on an in-page link, however, we want to use
 * `location.hash` to set the new URL instead of `history.pushState()`
 * for a few reasons:
 *
 * * Using `location.hash` will invoke the sequential focus
 *   navigation behavior of browsers, which keeps things
 *   nice and accessible for keyboard users.
 *
 * * Using `history.pushState()` doesn't invoke `:target`
 *   CSS selectors, at the time of this writing, which is
 *   unfortunate (for more details, see
 *   https://bugs.webkit.org/show_bug.cgi?id=83490).
 *
 * However, we still want to store the current scroll
 * offset for the new history entry, so to do that we'll
 * wait for the `hashchange` event to fire and then use
 * `history.replaceState()`.
 */

// This is the amount of time, in milliseconds, that we'll take to
// scroll the page from its current position to a new position.
const SCROLL_MS = 500;

function rememberCurrentScrollPosition() {
  window.history.replaceState({
    pageYOffset: window.pageYOffset,
  }, '');
}

function changeHash(hash, cb) {
  const currId = window.location.hash.slice(1);
  const newId = hash.slice(1);

  if (currId !== newId) {
    $(window).one('hashchange', cb);
  }
  window.location.hash = hash;
}

if (window.history && window.history.replaceState) {
  $('body').on('click', 'a[href^="#"]', e => {
    const scrollId = $(e.target).attr('href').slice(1);
    const scrollTarget = document.getElementById(scrollId);
    let doneAnimating = false;

    if (scrollTarget) {
      e.preventDefault();
      rememberCurrentScrollPosition();
      $('html, body').animate({
        scrollTop: $(scrollTarget).offset().top,
      }, SCROLL_MS, () => {
        // This callback is going to be called multiple times because
        // we're animating on multiple elements, but we only want the
        // code to execute once--hence our use of `doneAnimating`.

        if (!doneAnimating) {
          doneAnimating = true;
          changeHash(`#${scrollId}`, rememberCurrentScrollPosition);
        }
      });
    }
  });

  window.addEventListener('popstate', e => {
    if (e.state && 'pageYOffset' in e.state) {
      $('html, body').animate({
        scrollTop: e.state.pageYOffset,
      }, SCROLL_MS);
    }
  }, false);

  // https://developers.google.com/web/updates/2015/09/history-api-scroll-restoration
  if ('scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'manual';
  }
}
