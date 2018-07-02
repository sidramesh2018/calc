/* eslint-env browser */
/* global QUnit document */

import * as validation from '../data-capture/form-validation';

import * as sinon from 'sinon';

QUnit.module('form-validation');

class FakeForm {
  constructor(options = {}) {
    Object.assign(this, {
      checkValidity: sinon.stub(),
      submit: sinon.stub(),
    });
  }
}

class FakeWindow {
  constructor(options = {}) {
    Object.assign(this, {
      history: {
        state: options.state || null,
        replaceState(state) {
          this.state = state;
        },
      },
      location: {
        hash: '',
      },
      document: {
        body: { scrollTop: 0 },
        documentElement: { scrollTop: 0 },
        readyState: options.readyState || 'loading',
        getElementById() { return null; },
        getElementsByTagName: sinon.stub(),
        querySelectorAll: sinon.stub(),
        querySelector: sinon.stub(),
      },
      sessionStorage: options.sessionStorage || {},
      listeners: {},
    });
  }

  addEventListener(type, cb) {
    if (type in this.listeners) {
      throw new Error('only one listener per type expected');
    }
    this.listeners[type] = cb;
  }
}


function makeInputSet(isDate = true) {
  const groupedFieldset = document.createElement('fieldset');
  const input1 = document.createElement('input');
  const input2 = document.createElement('input');
  let subgroup = document.createElement('div');

  if (isDate) {
    subgroup = document.createElement('uswds-date');
  }

  subgroup.appendChild(input1);
  subgroup.appendChild(input2);
  groupedFieldset.appendChild(subgroup);

  return {groupedFieldset, subgroup, input1, input2};
}

function makeInput() {
  const fieldset = document.createElement('fieldset');
  const input = document.createElement('input');
  fieldset.appendChild(input);

  return {fieldset, input};
}

QUnit.test('getCustomMessage works', (assert) => {
  const ERROR_MESSAGES = {
    valueMissing: 'Please fill out this required field.',
  };

  const invalidValue = {
    typeMismatch: false,
    valueMissing: true,
  };

  const validInput = {
    typeMismatch: false,
    valueMissing: false,
  };

  assert.equal(validation.getCustomMessage('text', invalidValue), ERROR_MESSAGES.valueMissing);
  assert.equal(validation.getCustomMessage('text', validInput), undefined);
});

QUnit.test('findParentNode works', (assert) => {
  const FIELD_PARENT_NODE = 'fieldset';
  // simple inputs
  const singleFieldParent = document.createElement('fieldset');
  const singleField = document.createElement('input');

  singleFieldParent.appendChild(singleField);

  // compound inputs
  const {groupedFieldset, input1} = makeInputSet();

  // inputs not wrapped in `fieldset`
  const faultyInputBody = document.createElement('body');
  const faultyInputParent = document.createElement('div');
  const faultyInput = document.createElement('input');
  faultyInputParent.appendChild(faultyInput);
  faultyInputBody.appendChild(faultyInputParent);

  assert.equal(validation.findParentNode(singleField), singleFieldParent);
  assert.equal(validation.findParentNode(input1), fieldset);
  assert.equal(validation.findParentNode(faultyInput), null);
});

QUnit.skip('toggleErrorMsg works', (assert) => {
  const INVALID_MESSAGE_CLASS = 'form--invalid__message';
  const INVALID_PARENT_CLASS = 'fieldset__form--invalid';

});


QUnit.test('domContentLoaded', (assert) => {
  let win = new FakeWindow();
  validation.window = win;

  let fakeForm = new FakeForm();

  let fakeSubmitButton = {
    addEventListener: sinon.stub(),
  };

  let input = makeInput().input;

  win.document.getElementsByTagName.withArgs('form').returns([fakeForm]);
  win.document.querySelectorAll.withArgs('input, select, textarea').returns([input]);
  win.document.querySelector.withArgs('.submit-group button[type="submit"]').returns(fakeSubmitButton);

  fakeForm.checkValidity.returns(true);

  const result = validation.domContentLoaded(win);
  assert.ok(fakeSubmitButton.addEventListener.calledWith('click'));
  assert.ok(fakeForm.checkValidity.called);
});

