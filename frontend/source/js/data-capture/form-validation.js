/* global $, window */

/**
 * HTML5 form validation doesn't apply our styles. Documented here:
 * https://github.com/18F/calc/issues/2017
 * This implementation is mostly taken from
 * https://pageclip.co/blog/2018-02-20-you-should-use-html5-form-validation.html
 */

const INVALID_CLASS = 'form--invalid';
const INVALID_MESSAGE_CLASS = 'form--invalid__message';
const FIELD_PARENT_NODE = 'fieldset';
const INVALID_PARENT_CLASS = 'fieldset__form--invalid';
const ERROR_MESSAGES = {
  valueMissing: 'Please fill out this required field.',
};


function getCustomMessage (type, validity) {
  if (validity.typeMismatch) {
    return ERROR_MESSAGES[`${type}Mismatch`];
  } else {
    for (const invalidKey in ERROR_MESSAGES) {
      if (validity[invalidKey]) {
        return ERROR_MESSAGES[invalidKey];
      }
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('input, select, textarea');

  inputs.forEach(function (input) {
    if (input.type != 'hidden') {
      // Radio buttons, inputs and USWDS date fields have deep nesting structures.
      // We need to find the `fieldset` that contains the input in question and
      // set the error message on that, otherwise we end up with multiple messages.
      // Because we're using django-uswds-forms, 
      function findParentNode(node) {
        if (node.parentNode.tagName != 'FIELDSET') {
          return findParentNode(node.parentNode);
        } else {
          return node.parentNode;
        }
      }

      function toggleErrorMessage(options) {
        const parent = findParentNode(input);
        const errorContainer = parent.querySelector(`.${INVALID_MESSAGE_CLASS}`)
          ||  document.createElement('p');
        // grouped inputs like radios have legends; single inputs just have labels
        const fieldsetLabel = parent.getElementsByTagName('legend')[0] || parent.getElementsByTagName('label')[0];

        if (!input.validity.valid && input.validationMessage) {
          errorContainer.className = INVALID_MESSAGE_CLASS;
          errorContainer.textContent = input.validationMessage;

          if (options.showErrorMsg) {
            parent.insertBefore(errorContainer, fieldsetLabel);
            parent.classList.add(INVALID_PARENT_CLASS);
          }
        } else {
          parent.classList.remove(INVALID_PARENT_CLASS);
          errorContainer.remove();
        }
      }

      function setValidityClass(options) {
        input.validity.valid
        ? input.classList.remove(INVALID_CLASS)
        : input.classList.add(INVALID_CLASS);

        toggleErrorMessage(options);
      }

      // Each time the user submits, this will set a custom message if invalid.
      function checkValidity (options) {
        const message = input.validity.valid
          ? null
          : getCustomMessage(input.type, input.validity);

        input.setCustomValidity(message || '');
        setValidityClass(options);
      }

      input.addEventListener('invalid', function (e) {
        // prevent showing the HTML5 tooltip
        e.preventDefault();
        checkValidity({showErrorMsg: true});
      });
    }
  });
});
