/* global window, document */

// The following feature detectors are ultimately pulled from Modernizr.

module.exports = {
  dragAndDrop() {
    const div = document.createElement('div');
    return ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div);
  },

  formData() {
    return 'FormData' in window;
  },

  dataTransfer() {
    // Browsers that support FileReader support DataTransfer too.
    return 'FileReader' in window;
  },
};
