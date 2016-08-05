/* global QUnit $ test window */

const urlParse = require('url').parse;
const sinon = require('sinon');

const step1 = window.testingExports__step_1;

let server;

QUnit.module('step_1', {
  beforeEach() {
    server = sinon.fakeServer.create();
    $('[data-step1-form]').remove();
  },
  afterEach() {
    $('[data-step1-form]').remove();
    server.restore();
  },
});

function createBlob(content) {
  if (typeof(window.Blob) === 'function') {
    return new window.Blob([content]);
  }

  // We're in PhantomJS.
  const builder = new window.WebKitBlobBuilder();
  builder.append(content);
  return builder.getBlob();
}

function advancedTest(name, cb) {
  if (!$.support.advancedUpload) {
    return QUnit.skip(name, cb);
  }
  return QUnit.test(name, cb);
}

function addForm(extraOptions) {
  const options = Object.assign({
    uploadAttrs: '',
  }, extraOptions || {});

  const FORM_HTML = `
    <form enctype="multipart/form-data" method="post"
          data-step1-form
          action="/post-stuff">
      <input type="text" name="foo" value="bar">
      <div class="upload" ${options.uploadAttrs}>
        <input type="file" name="file"
               id="id_file" accept=".xlsx,.xls,.csv">
        <div class="upload-chooser">
          <label for="id_file">Choose file</label>
          <span class="js-only" aria-hidden="true">or drag+drop here.</span>
          XLS, XLSX, or CSV format, please.
        </div>
      </div>
      <button type="submit">submit</button>
    </form>
  `;

  $('<div></div>').html(FORM_HTML).appendTo('body').hide();
  return step1.bindForm();
}

test('bindForm() returns null when data-step1-form not on page', assert => {
  assert.strictEqual(step1.bindForm(), null);
});

test('submit btn disabled on startup', assert => {
  assert.ok(addForm().$submit.prop('disabled'));
});

test('submit btn enabled on file input change', assert => {
  const s = addForm();

  s.$fileInput.trigger('change');
  assert.ok(!s.$submit.prop('disabled'), 'submit button is enabled');
});

test('submit btn enabled on upload widget changefile', assert => {
  const s = addForm();

  s.$fileInput.trigger('changefile', { name: 'baz' });
  assert.ok(!s.$submit.prop('disabled'), 'submit button is enabled');
});

test('degraded input does not cancel form submission', assert => {
  const s = addForm({ uploadAttrs: 'data-force-degradation' });

  $(s.form).on('submit', e => {
    assert.ok(!e.isDefaultPrevented());
    e.preventDefault();
  });

  $(s.form).submit();
});

advancedTest('submit triggers ajax w/ form data', assert => {
  const s = addForm();

  $(s.form).on('submit', e => {
    assert.ok(e.isDefaultPrevented());
    assert.equal(server.requests.length, 1);

    const req = server.requests[0];
    const formData = req.requestBody;

    assert.equal(req.method, 'POST');
    assert.equal(urlParse(req.url).path, '/post-stuff');

    // Ugh, only newer browsers support FormData.prototype.get().
    if (typeof(formData.get) === 'function') {
      assert.equal(formData.get('foo'), 'bar');
      assert.equal(formData.get('file').size, 'hello there'.length);
    }
  });

  s.upload.file = createBlob('hello there');

  $(s.form).submit();
});
