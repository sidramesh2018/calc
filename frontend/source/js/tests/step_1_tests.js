/* global QUnit $ test window */

const step1 = window.testingExports__step_1;

QUnit.module('step_1', {
  beforeEach() {
    $('[data-step1-form]').remove();
  },
  afterEach() {
    $('[data-step1-form]').remove();
  },
});

const FORM_HTML = `
  <form enctype="multipart/form-data" method="post"
        data-step1-form
        action="/post-stuff">
    <input type="text" name="foo" value="bar">
    <div class="upload">
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

function addForm() {
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
