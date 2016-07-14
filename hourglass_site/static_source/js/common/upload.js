/* global $ */
/* eslint-disable prefer-arrow-callback, func-names */

$(document).ready(function () {
  // The following feature detectors are ultimately pulled from Modernizr.

  function browserSupportsDragAndDrop() {
    var div = document.createElement('div');
    return ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div);
  }

  function browserSupportsFormData() {
    return 'FormData' in window;
  }

  function browserSupportsDataTransfer() {
    // Browsers that support FileReader support DataTransfer too.
    return 'FileReader' in window;
  }

  function browserSupportsAdvancedUpload() {
    return browserSupportsDragAndDrop() && browserSupportsFormData() &&
           browserSupportsDataTransfer();
  }

  function stopAndPrevent(event) {
    event.stopPropagation();
    event.preventDefault();
  }

  $('.upload').each(function () {
    var $el = $(this);
    var $input = $('input', $el);
    var self = {
      isDegraded: false,
      file: null
    };

    function setCurrentFilename(filename) {
      $('input', $el).nextAll().remove();

      var id = $('input', $el).attr('id');
      var current = $(
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

    $input.data('upload', self);

    if (!browserSupportsAdvancedUpload() ||
        this.hasAttribute('data-force-degradation')) {
      $el.addClass('degraded');
      self.isDegraded = true;
      return;
    }

    $el.on('dragenter', stopAndPrevent);
    $el.on('dragover', stopAndPrevent);
    $el.on('drop', function (e) {
      stopAndPrevent(e);

      var dt = e.originalEvent.dataTransfer;
      var files = dt.files;

      if (files.length > 0) {
        $el.trigger('changefile', files[0]);
      }
    });

    $input.on('change', function () {
      var selectedFile = this.files[0];

      if (selectedFile) {
        $el.trigger('changefile', selectedFile);
      }
    });

    $el.on('changefile', function (e, file) {
      self.file = file;
      $input.val('');
      setCurrentFilename(file.name);
    });
  });
});
