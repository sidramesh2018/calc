/* eslint-env browser */
/* global QUnit document */

import * as validation from '../data-capture/form-validation';

QUnit.module('form-validation');

function makeInputSet() {
  const date = document.createElement('uswds-date');
  const input1 = document.createElement('input');
  const input2 = document.createElement('input');

  date.appendChild(input1);
  date.appendChild(input2);

  return {date, input1, input2};
}

function makeForm() {
  const form = document.createElement('form');
  const textInput = document.createElement('input');
  textInput.type = 'text';
  const radioInput = document.createElement('input');
  radioInput.type = 'radio';
  const checkboxInput = document.createElement('input');
  checkboxInput.type = 'checkbox';
  const dateInput = makeInputSet().date;

  // Note that inputs is a NodeList in the live code, but is transformed into an array. For simplicity, just make a dummy array.
  const inputs = [
    textInput,
    radioInput,
    checkboxInput,
    dateInput,
    document.createElement('select'),
    document.createElement('textarea')
  ];

  const submitButton = document.createElement('button');
  submitButton.type = 'submit';

  inputs.forEach((input) => form.appendChild(input));
  form.appendChild(submitButton);

  return {form, inputs, submitButton};
}

QUnit.test('single inputs are extracted correctly', (assert) => {
  assert.expect(5);
  const inputs = makeForm().inputs;
  const singles = window.parseInputs(inputs).singleInputs;
  // test inputs minus uswds-date input
  const singlesTest = inputs.splice(3,1);
  assert.equal(singles, singlesTest);
});

QUnit.test('compound inputs are extracted correctly', (assert) => {
  assert.expect(1);
  const inputs = makeForm().inputs;
  const compound = window.parseInputs(inputs).combinedInputs;
  // just the uswds-date input
  const compoundTest = inputs[3];
  assert.equal(compound, compoundTest);
});
