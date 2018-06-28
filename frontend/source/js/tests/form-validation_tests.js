/* eslint-env browser */
/* global QUnit document */

import * as validation from '../data-capture/form-validation';

import * as sinon from 'sinon';

QUnit.module('form-validation');

QUnit.test('getCustomMessage works', (assert) => {
  const ERROR_MESSAGES = {
    valueMissing: 'Please fill out this required field.',
  };

  let invalidValue = {
    typeMismatch: false,
    valueMissing: true,
  };

  let validInput = {
    typeMismatch: false,
    valueMissing: false,
  };

  assert.equal(validation.getCustomMessage('text', invalidValue), ERROR_MESSAGES.valueMissing);
  assert.equal(validation.getCustomMessage('text', validInput), undefined);
});
