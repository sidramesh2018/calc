/* global $ */
/* eslint-disable prefer-arrow-callback, func-names */

$(document).ready(function () {
  // https://css-tricks.com/drag-and-drop-file-uploading/
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
    var self = $(this);

    function setCurrentFilename(filename) {
      $('input', self).nextAll().remove();

      var id = $('input', self).attr('id');
      var current = $(
        '<div class="upload-current">' +
        '<div class="upload-filename"></div>' +
        '<div class="upload-changer">Not right? ' +
        '<label>Choose a different file</label> or drag and drop here.' +
        '</div></div>'
      );
      $('label', current).attr('for', id);
      $('.upload-filename', current).text(filename);
      self.append(current);
    }

    if (!browserSupportsAdvancedUpload()) {
      self.addClass('degraded');
      return;
    }

    self.on('dragenter', stopAndPrevent);
    self.on('dragover', stopAndPrevent);
    self.on('drop', function (e) {
      stopAndPrevent(e);

      var dt = e.originalEvent.dataTransfer;
      var files = dt.files;

      if (files.length > 0) {
        self.trigger('changefile', files[0]);
      }
    });

    $('input').on('change', function () {
      var selectedFile = this.files[0];

      if (selectedFile) {
        self.trigger('changefile', selectedFile);
      }
    });
  });
});
