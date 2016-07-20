(function(QUnit, $) {
  var UPLOAD_HTML = (
    '<div class="upload">' +
    '<input type="file" name="file" id="file" accept=".csv, application/test">' +
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

    assert.ok(upload.hasClass('degraded'));
    assert.ok(!upload[0].hasAttribute('aria-live'));
    assert.strictEqual(input.data('upload').isDegraded, true);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("extra calls to uploadify() do nothing", function(assert) {
    var data = input.data('upload');
    upload.uploadify();
    assert.strictEqual(input.data('upload'), data);
  });

  advancedTest("advanced upload sets aria-live", function(assert) {
    assert.equal(upload.attr("aria-live"), "polite");
  });

  advancedTest("advanced upload sets 'upload' data", function(assert) {
    assert.strictEqual(input.data('upload').isDegraded, false);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("advanced upload does not allow non-accepted file types", function(assert) {
    var badFakeFile = {name: "boop", type: "application/badtest"};
    var evt = jQuery.Event('drop', {
      originalEvent: { dataTransfer: { files: [badFakeFile] } }
    });

    upload.trigger(evt);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("advanced upload allows accepted file types", function(assert) {
    var goodFileMime = {name: "boop", type: "application/test"};
    var evt = jQuery.Event('drop', {
      originalEvent: { dataTransfer: { files: [goodFileMime] } }
    });

    upload.trigger(evt);
    assert.strictEqual(input.data('upload').file, goodFileMime);

    var goodFileExt = {name: "boop.csv", type: "whatever"};
    evt = jQuery.Event('drop', {
     originalEvent: { dataTransfer: { files: [goodFileExt] } }
    });
    upload.trigger(evt);
    assert.strictEqual(input.data('upload').file, goodFileExt);

  });


  advancedTest("'changefile' event triggered on drop", function(assert) {
    var fakeFile = {name: "boop", type: "application/test"};
    var evt = jQuery.Event('drop', {
      originalEvent: { dataTransfer: { files: [fakeFile] } }
    });

    upload.on('changefile', function(e, file) {
      assert.strictEqual(file, fakeFile);
    });
    upload.trigger(evt);
  });

  advancedTest("input 'change' evt w/o files does nothing", function(assert) {
    input.trigger('change');
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest("'changefile' sets current file", function(assert) {
    var fakeFile = {name: "foo.txt", type: "application/test"};
    input.trigger('changefile', fakeFile);

    assert.strictEqual(input.data('upload').file, fakeFile);
    assert.equal(upload.find('.upload-filename').text(), 'foo.txt');
  });

  advancedTest("dragenter/dragleave affect .dragged-over", function(assert) {
    var i;

    assert.ok(!upload.hasClass('dragged-over'));

    for (i = 0; i < 3; i++) {
      upload.trigger('dragenter');
      assert.ok(upload.hasClass('dragged-over'));
    }

    for (i = 0; i < 2; i++) {
      upload.trigger('dragleave');
      assert.ok(upload.hasClass('dragged-over'));
    }

    upload.trigger('dragleave');
    assert.ok(!upload.hasClass('dragged-over'));
  });
})(QUnit, jQuery);
