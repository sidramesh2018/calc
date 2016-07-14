(function(QUnit, $) {
  QUnit.module("upload");

  var UPLOAD_HTML = (
    '<div class="upload">' +
    '<input type="file" name="file" id="file">' +
    '<div class="upload-chooser">' +
    '<label for="file">Choose file or drag and drop here</label>' +
    '</div>' +
    '</div>'
  );

  var advancedTest = $.support.advancedUpload ? QUnit.test : QUnit.skip;

  test("degraded upload sets 'upload', data", function(assert) {
    var upload = $(UPLOAD_HTML)
      .attr('data-force-degradation', 'yup')
      .appendTo(document.body);

    var input = upload.uploadify().find('input');

    assert.strictEqual(input.data('upload').isDegraded, true);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);

    upload.remove();
  });

  advancedTest("advanced upload sets 'upload' data", function(assert) {
    var upload = $(UPLOAD_HTML).appendTo(document.body);

    var input = upload.uploadify().find('input');

    assert.strictEqual(input.data('upload').isDegraded, false);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);

    upload.remove();
  });
})(QUnit, jQuery);
