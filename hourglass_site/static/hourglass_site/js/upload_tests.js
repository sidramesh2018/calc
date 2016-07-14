(function(QUnit, $) {
  var UPLOAD_HTML = (
    '<div class="upload">' +
    '<input type="file" name="file" id="file">' +
    '<div class="upload-chooser">' +
    '<label for="file">Choose file or drag and drop here</label>' +
    '</div>' +
    '</div>'
  );

  var upload, input;

  function advancedTest(name, cb) {
    if (!$.support.advancedUpload) {
      return QUnit.skip(name, cb);
    }
    return QUnit.test(name, function(assert) {
      upload = $(UPLOAD_HTML).appendTo(document.body);
      input = upload.uploadify().find('input');
      return cb(assert);
    });
  }

  QUnit.module("upload", {
    afterEach: function() {
      if (upload) {
        upload.remove();
      }
      upload = null;
      input = null;
    }
  });

  test("$.support.advancedUpload is a boolean", function(assert) {
    assert.equal(typeof($.support.advancedUpload), "boolean");
  });

  test("degraded upload sets 'upload', data", function(assert) {
    upload = $(UPLOAD_HTML)
      .attr('data-force-degradation', 'yup')
      .appendTo(document.body);
    input = upload.uploadify().find('input');

    assert.strictEqual(input.data('upload').isDegraded, true);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("advanced upload sets 'upload' data", function(assert) {
    assert.strictEqual(input.data('upload').isDegraded, false);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("'changefile' event triggered on drop", function(assert) {
    var fakeFile = {name: "boop"};
    var evt = jQuery.Event('drop', {
      originalEvent: { dataTransfer: { files: [fakeFile] } }
    });

    upload.on('changefile', function(e, file) {
      assert.strictEqual(file, fakeFile);
    });
    upload.trigger(evt);
  });
})(QUnit, jQuery);
