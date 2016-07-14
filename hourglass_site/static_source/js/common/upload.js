/* global $ */
/* eslint-disable prefer-arrow-callback, func-names */

(function ($) {
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

  function activateUploadWidget($el) {
    var $input = $('input', $el);
    var dragCounter = 0;
    var self = {
      input: $input[0],
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

    if ($input.data('upload')) {
      // We've already been uploadified!
      return;
    }

    $input.data('upload', self);

    if (!browserSupportsAdvancedUpload() ||
        $el[0].hasAttribute('data-force-degradation')) {
      $el.addClass('degraded');
      self.isDegraded = true;
      return;
    }

    $el.on('dragenter', function (e) {
      stopAndPrevent(e);

      dragCounter++;
      $el.addClass('dragged-over');
    });
    $el.on('dragleave', function (e) {
      // http://stackoverflow.com/a/21002544/2422398
      if (--dragCounter === 0) {
        $el.removeClass('dragged-over');
      }
    });
    $el.on('dragover', stopAndPrevent);
    $el.on('drop', function (e) {
      stopAndPrevent(e);
      $el.removeClass('dragged-over');

      var dt = e.originalEvent.dataTransfer;
      var files = dt.files;

      if (files.length > 0) {
        $input.trigger('changefile', files[0]);
      }
    });

    $input.on('change', function () {
      var selectedFile = this.files[0];

      if (selectedFile) {
        $input.trigger('changefile', selectedFile);
      }
    });

    $input.on('changefile', function (e, file) {
      self.file = file;
      $input.val('');
      setCurrentFilename(file.name);
    });
  }

  $.fn.uploadify = function() {
    this.each(function() {
      activateUploadWidget($(this));
    });
  };

  $(document).ready(function() {
    $('.upload').uploadify();
  });
})(jQuery);
