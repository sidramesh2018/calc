/* global document, window */

// The following code is based off:
// https://github.com/d4tocchini/customevent-polyfill

try {
  /* eslint-disable no-new */
  new window.CustomEvent('test');
  /* eslint-enable no-new */
} catch (e) {
  const CustomEvent = (event, originalParams) => {
    const params = Object.assign({
      bubbles: false,
      cancelable: false,
      detail: undefined,
    }, originalParams || {});

    const evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(event, params.bubbles, params.cancelable,
                        params.detail);
    return evt;
  };

  CustomEvent.prototype = window.Event.prototype;
  window.CustomEvent = CustomEvent; // expose definition to window
}

exports.dispatchBubbly = (el, eventType, params) => {
  el.dispatchEvent(new window.CustomEvent(eventType, Object.assign({
    bubbles: true,
  }, params || {})));
};
