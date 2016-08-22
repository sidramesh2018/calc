/* global QUnit $ test document window QUNIT_FIXTURE_DATA */

const urlParse = require('url').parse;
const sinon = require('sinon');

const ajaxform = window.testingExports__ajaxform;

let server;
let $parentDiv;

QUnit.module('ajaxform', {
  beforeEach() {
    server = sinon.fakeServer.create();
  },
  afterEach() {
    server.restore();
    if ($parentDiv) {
      $parentDiv.remove();
      $parentDiv = null;
    }
  },
});

function createBlob(content) {
  // If in PhantomJS 1.x
  if (window.WebKitBlobBuilder) {
    const builder = new window.WebKitBlobBuilder();
    builder.append(content);
    return builder.getBlob();
  }

  // In a more modern engine with Blob support
  if (window.Blob) {
    return new window.Blob([content]);
  }

  throw new Error('Unable to determine how to create Blob');
}

function makeFormHtml(extraOptions) {
  const options = Object.assign({
    isDegraded: false,
    fooValue: 'bar',
  }, extraOptions || {});

  const iframe = document.createElement('iframe');

  document.body.appendChild(iframe);

  const $form = $(iframe.contentDocument.body)
    .html(QUNIT_FIXTURE_DATA.AJAXFORM_TESTS_HTML);

  if (options.isDegraded) {
    $form.find('form').attr('data-force-degradation', '');
  }

  $form.find('input[name="foo"]').attr('value', options.fooValue);

  $(iframe).remove();

  return $form.html();
}

function addForm(extraOptions, cb) {
  const div = $('<div></div>').appendTo('body').hide();
  const s = {
    setFile(file) {
      this.uploadwidget.file = file;
    },
  };

  $parentDiv = div;

  function update() {
    if (s.ajaxform && s.uploadwidget) {
      cb(s);
    }
  }

  div.one('uploadwidgetready', e => {
    s.uploadwidget = $('input', e.target).data('upload');
    update();
  });
  div.one('ajaxformready', e => {
    s.ajaxform = $(e.target).data('ajaxform');
    update();
  });
  div.html(makeFormHtml(extraOptions));
}

function formTest(name, options, originalCb) {
  let cb = originalCb;
  let extraOptions = options;

  if (!cb) {
    cb = extraOptions;
    extraOptions = undefined;
  }
  return QUnit.test(name, assert => {
    const done = assert.async();
    addForm(extraOptions, s => {
      cb(assert, s);
      done();
    });
  });
}

function advancedTest(name, extraOptions, cb) {
  if (!$.support.advancedUpload) {
    return QUnit.skip(name, cb);
  }
  return formTest(name, extraOptions, cb);
}

class FakeFormData {
  constructor() {
    this.appended = [];
  }

  append(name, value) {
    this.appended.push([name, value]);
  }
}

formTest('degraded form does not cancel form submission', {
  isDegraded: true,
}, (assert, s) => {
  $(s.ajaxform.form).on('submit', e => {
    assert.ok(s.ajaxform.isDegraded);
    assert.ok(!e.isDefaultPrevented());
    e.preventDefault();
  });

  $(s.ajaxform.form).submit();
});

test('populateFormData() works w/ non-upgraded file inputs', assert => {
  const formData = ajaxform.populateFormData({
    elements: [{
      type: 'file',
      name: 'boop',
      files: ['fakeFile'],
    }],
  }, new FakeFormData());

  assert.deepEqual(formData.appended, [['boop', 'fakeFile']]);
});

advancedTest('submit triggers ajax w/ form data', (assert, s) => {
  $(s.ajaxform.form).on('submit', e => {
    assert.ok(e.isDefaultPrevented());
    assert.equal(server.requests.length, 1);

    const req = server.requests[0];
    const formData = req.requestBody;

    assert.equal(req.method, 'POST');
    assert.equal(urlParse(req.url).path, '/post-stuff');

    // Ugh, only newer browsers support FormData.prototype.get().
    if (typeof formData.get === 'function') {
      assert.equal(formData.get('foo'), 'bar');
      assert.equal(formData.get('file').size, 'hello there'.length);
    }
  });

  s.setFile(createBlob('hello there'));

  $(s.ajaxform.form).submit();
});

advancedTest('form_html replaces form & rebinds it', {
  fooValue: 'hello',
}, (assert, s) => {
  function getForm() {
    const $form = $('form', $parentDiv);
    assert.equal($form.length, 1);
    return $form[0];
  }

  const origForm = getForm();

  assert.equal($('input[name="foo"]', origForm).val(), 'hello');

  s.setFile(createBlob('blah'));
  $(origForm).submit();

  server.requests[0].respond(
    200,
    { 'Content-Type': 'application/json' },
    JSON.stringify({
      form_html: makeFormHtml({ fooValue: 'blargyblarg' }),
    })
  );

  const newForm = getForm();

  assert.ok(newForm !== origForm);
  assert.equal($('input[name="foo"]', newForm).val(), 'blargyblarg');
});

advancedTest('redirect_url redirects browser', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform.form).submit();

  const delegate = ajaxform.setDelegate({ redirect: sinon.spy() });

  server.requests[0].respond(
    200,
    { 'Content-Type': 'application/json' },
    JSON.stringify({
      redirect_url: 'http://boop',
    })
  );

  assert.ok(delegate.redirect.calledWith('http://boop'));
});

advancedTest('500 results in alert', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform.form).submit();

  const delegate = ajaxform.setDelegate({ alert: sinon.spy() });

  server.requests[0].respond(500);

  assert.ok(delegate.alert.calledWith(ajaxform.MISC_ERROR));
});

advancedTest('unrecognized 200 results in alert', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform.form).submit();

  const delegate = ajaxform.setDelegate({ alert: sinon.spy() });

  server.requests[0].respond(200);

  assert.ok(delegate.alert.calledWith(ajaxform.MISC_ERROR));
});
