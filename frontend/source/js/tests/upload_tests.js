/* global QUnit jQuery document test QUNIT_FIXTURE_DATA */
(function uploadTests(QUnit, $) {
  const UPLOAD_HTML = QUNIT_FIXTURE_DATA.UPLOAD_TESTS_HTML;

  let $parentDiv;
  let upload;
  let input;

  function makeWidget(isDegraded, cb) {
    const div = document.createElement('div');

    $parentDiv = $(div);

    if (isDegraded) {
      div.setAttribute('data-force-degradation', '');
    }

    div.addEventListener('uploadwidgetready', e => {
      upload = $(e.target);
      input = upload.find('input');
      cb();
    });
    document.body.appendChild(div);
    div.innerHTML = UPLOAD_HTML;
  }

  function degradedTest(name, cb) {
    return QUnit.test(name, (assert) => {
      const done = assert.async();

      makeWidget(true, () => {
        cb(assert);
        done();
      });
    });
  }

  function advancedTest(name, cb) {
    if (!$.support.advancedUpload) {
      return QUnit.skip(name, cb);
    }
    return QUnit.test(name, (assert) => {
      const done = assert.async();

      makeWidget(false, () => {
        cb(assert);
        done();
      });
    });
  }

  QUnit.module('upload', {
    afterEach() {
      if ($parentDiv) {
        $parentDiv.remove();
        $parentDiv = null;
      }
      upload = null;
      input = null;
    },
  });

  test('$.support.advancedUpload is a boolean', (assert) => {
    assert.equal(typeof $.support.advancedUpload, 'boolean');
  });

  degradedTest('degraded upload sets "upload" data', (assert) => {
    assert.ok(upload.hasClass('degraded'));
    assert.ok(!upload[0].hasAttribute('aria-live'));
    assert.strictEqual(input.data('upload').isDegraded, true);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest('advanced upload sets aria-live', (assert) => {
    assert.equal(upload.attr('aria-live'), 'polite');
  });

  advancedTest('advanced upload sets "upload" data', (assert) => {
    assert.strictEqual(input.data('upload').isDegraded, false);
    assert.strictEqual(input.data('upload').input, input[0]);
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest('advanced upload does not allow non-accepted file types', (assert) => {
    const badFakeFile = { name: 'boop', type: 'application/badtest' };
    const evt = jQuery.Event('drop', { // eslint-disable-line new-cap
      originalEvent: { dataTransfer: { files: [badFakeFile] } },
    });

    upload.trigger(evt);
    assert.strictEqual(input.data('upload').file, null);
    assert.ok(upload.find('.upload-error').length);
  });

  advancedTest('advanced upload allows accepted file types', (assert) => {
    const goodFileMime = { name: 'boop', type: 'application/test' };
    const mimeDropEvt = jQuery.Event('drop', { // eslint-disable-line new-cap
      originalEvent: { dataTransfer: { files: [goodFileMime] } },
    });

    upload.trigger(mimeDropEvt);
    assert.strictEqual(input.data('upload').file, goodFileMime);

    const goodFileExt = { name: 'boop.csv', type: 'whatever' };
    const extDropEvt = jQuery.Event('drop', { // eslint-disable-line new-cap
      originalEvent: { dataTransfer: { files: [goodFileExt] } },
    });
    upload.trigger(extDropEvt);
    assert.strictEqual(input.data('upload').file, goodFileExt);
  });

  advancedTest('advanced upload allows any file when "accept" not specified', (assert) => {
    input.attr('accept', null);
    const fakeFile = { name: 'boop' };
    const evt = jQuery.Event('drop', { // eslint-disable-line new-cap
      originalEvent: { dataTransfer: { files: [fakeFile] } },
    });
    upload.trigger(evt);
    assert.strictEqual(input.data('upload').file, fakeFile);
  });

  advancedTest('"changefile" event triggered on drop', (assert) => {
    const fakeFile = { name: 'boop', type: 'application/test' };
    const evt = jQuery.Event('drop', { // eslint-disable-line new-cap
      originalEvent: { dataTransfer: { files: [fakeFile] } },
    });

    upload.on('changefile', (e, file) => {
      assert.strictEqual(file, fakeFile);
    });
    upload.trigger(evt);
  });

  advancedTest('input "change" evt w/o files does nothing', (assert) => {
    input.trigger('change');
    assert.strictEqual(input.data('upload').file, null);
  });

  advancedTest('"changefile" sets current file', (assert) => {
    const fakeFile = { name: 'foo.txt', type: 'application/test' };
    input.trigger('changefile', fakeFile);

    assert.strictEqual(input.data('upload').file, fakeFile);
    assert.equal(upload.find('.upload-filename').text(), 'foo.txt');
  });

  advancedTest('dragenter/dragleave affect .dragged-over', (assert) => {
    assert.ok(!upload.hasClass('dragged-over'));

    for (let i = 0; i < 3; i++) {
      upload.trigger('dragenter');
      assert.ok(upload.hasClass('dragged-over'));
    }

    for (let i = 0; i < 2; i++) {
      upload.trigger('dragleave');
      assert.ok(upload.hasClass('dragged-over'));
    }

    upload.trigger('dragleave');
    assert.ok(!upload.hasClass('dragged-over'));
  });
}(QUnit, jQuery));
