/* global QUnit document */

QUnit.module('collapsible-area');

QUnit.test('is not upgraded when empty', assert => {
  const ca = document.createElement('collapsible-area');
  ca.attachedCallback();
  assert.strictEqual(ca.isUpgraded, false);
});

function makeArea() {
  const ca = document.createElement('collapsible-area');
  const h1 = document.createElement('h1');
  ca.appendChild(h1);
  ca.attachedCallback();

  return { ca, h1 };
}

QUnit.test('is upgraded whenc containing at least one element', assert => {
  const { ca } = makeArea();
  assert.strictEqual(ca.isUpgraded, true);
});

QUnit.test('adds accessibility markup when upgraded', assert => {
  const { h1 } = makeArea();
  assert.equal(h1.getAttribute('aria-expanded'), 'false');
  assert.equal(h1.getAttribute('role'), 'button');
  assert.equal(h1.getAttribute('tabindex'), '0');
});

QUnit.test('toggle() flips aria-expanded value', assert => {
  const { ca, h1 } = makeArea();
  ca.toggle();
  assert.equal(h1.getAttribute('aria-expanded'), 'true');
  ca.toggle();
  assert.equal(h1.getAttribute('aria-expanded'), 'false');
});

QUnit.test('emits collapsibleareaready event', assert => {
  const done = assert.async();

  const fixture = document.getElementById('qunit-fixture');
  const div = document.createElement('div');

  div.addEventListener('collapsibleareaready', () => {
    fixture.removeChild(div);
    assert.ok(true, 'collapsibleareaready received');
    done();
  });

  div.innerHTML = '<collapsible-area><h1>hi</h1></collapsible-area>';

  fixture.appendChild(div);
});
