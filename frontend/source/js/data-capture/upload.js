/* global jQuery, window, document */

import 'document-register-element';

import * as supports from './feature-detection';

import { dispatchBubbly } from './custom-event';

const $ = jQuery;

class UploadInput extends window.HTMLInputElement {
  createdCallback() {
    if (this.getAttribute('type') !== 'file') {
      throw new Error('<input is="upload-input"> must have type "file".');
    }
    dispatchBubbly(this, 'uploadinputready');
  }

  get isUpgraded() {
    const upload = $(this).data('upload');

    return upload && !upload.isDegraded;
  }

  get upgradedValue() {
    const upload = $(this).data('upload');

    return upload && upload.file;
  }
}

function browserSupportsAdvancedUpload() {
  return supports.dragAndDrop() && supports.formData() &&
         supports.dataTransfer();
}

function stopAndPrevent(event) {
  event.stopPropagation();
  event.preventDefault();
}

function activateUploadWidget($el) {
  const $input = $('input', $el);
  const self = {
    input: $input[0],
    isDegraded: false,
    file: null,
  };
  let dragCounter = 0;

  function dispatchReadyEvent() {
    if (self.input instanceof UploadInput) {
      dispatchBubbly($el[0], 'uploadwidgetready');
    } else {
      $el.one('uploadinputready', dispatchReadyEvent);
    }
  }

  function setCurrentFilename(filename) {
    $('input', $el).nextAll().remove();

    const id = $('input', $el).attr('id');
    const current = $(
      '<div class="upload-current">' +
      '<div class="upload-filename"></div>' +
      '<div class="upload-changer">Not right? ' +
      '<label>Choose a different file</label> or drag and drop here.' +
      '</div></div>'
    );
    $('label', current).attr('for', id);
    $('.upload-filename', current).text(filename);
    $el.append(current);
  }

  function showInvalidFileMessage() {
    $('input', $el).nextAll().remove();

    const id = $('input', $el).attr('id');
    const err = $(
      '<div class="upload-error">' +
      '<div class="upload-error-message">Sorry, that type of file is not allowed.</div>' +
      'Please <label>choose a different file</label> or drag and drop one here.' +
      '</div></div>'
    );
    $('label', err).attr('for', id);
    $el.append(err);
  }

  function isFileValid(file) {
    const accepts = $input.attr('accept');
    if (!accepts || !accepts.length) {
      // nothing specified, so just return true
      return true;
    }
    const fileType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();
    const acceptsList = accepts.split(',').map((s) => s.trim().toLowerCase());
    for (const extOrType of acceptsList) {
      if (fileType === extOrType || fileName.lastIndexOf(extOrType,
        fileName.length - extOrType.length) !== -1) {
        return true;
      }
    }
    return false;
  }

  function setFile(file) {
    if (!file) { return; }
    if (!isFileValid(file)) {
      showInvalidFileMessage();
      return;
    }
    // else
    $input.trigger('changefile', file);
  }

  $input.data('upload', self);

  if (!browserSupportsAdvancedUpload() ||
      $el.closest('[data-force-degradation]').length) {
    $el.addClass('degraded');
    self.isDegraded = true;
    return dispatchReadyEvent();
  }

  $('label', $el)
    .after('<span aria-hidden="true"> or drag and drop here.</span>');

  // The content of the upload widget will change when the user chooses
  // a file, so let's make sure screen readers let users know about it.
  $el.attr('aria-live', 'polite');

  $el.on('dragenter', e => {
    stopAndPrevent(e);

    dragCounter++;
    $el.addClass('dragged-over');
  });
  $el.on('dragleave', () => {
    // http://stackoverflow.com/a/21002544/2422398
    if (--dragCounter === 0) {
      $el.removeClass('dragged-over');
    }
  });
  $el.on('dragover', stopAndPrevent);
  $el.on('drop', e => {
    stopAndPrevent(e);
    $el.removeClass('dragged-over');

    setFile(e.originalEvent.dataTransfer.files[0]);
  });

  $input.on('change', () => {
    setFile($input[0].files[0]);
  });

  $input.on('changefile', (e, file) => {
    self.file = file;
    $input.val('');
    setCurrentFilename(file.name);
  });

  return dispatchReadyEvent();
}

$.support.advancedUpload = browserSupportsAdvancedUpload();

class UploadWidget extends window.HTMLElement {
  createdCallback() {
    activateUploadWidget($(this));
  }
}

document.registerElement('upload-widget', {
  prototype: UploadWidget.prototype,
});

document.registerElement('upload-input', {
  extends: 'input',
  prototype: UploadInput.prototype,
});
