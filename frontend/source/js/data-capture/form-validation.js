/* global window */

/**
 * HTML5 form validation doesn't apply our styles. Documented here:
 * https://github.com/18F/calc/issues/2017
 * This implementation is mostly taken from
 * https://pageclip.co/blog/2018-02-20-you-should-use-html5-form-validation.html
 */

const INVALID_MESSAGE_CLASS = 'form--invalid__message';
const FIELD_PARENT_NODE = 'fieldset';
const INVALID_PARENT_CLASS = 'fieldset__form--invalid';
// We can expand this list as needed depending on which errors we need messaging for.
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

// Radio buttons, inputs and USWDS date fields have deep nesting structures.
// We need to find the `fieldset` that contains the input in question and
// set the error message on that, otherwise we end up with multiple messages.
// Because we're using django-uswds-forms, every form should be encapsulated
// in a fieldset automatically.
function findParentNode(node) {
  // tagName is always uppercase
  if (node.parentNode.tagName != FIELD_PARENT_NODE.toUpperCase() && node.parentNode.tagName != 'BODY') {
    return findParentNode(node.parentNode);
  } else if (node.parentNode.tagName == 'BODY') {
    // just in case we can't find the parent node, prevent infinite loop
    return null;
  } else {
    return node.parentNode;
  }
}

function toggleErrorMsg(options, node) {
  const parent = findParentNode(node);

  if (parent) {
    const errorContainer = parent.querySelector(`.${INVALID_MESSAGE_CLASS}`)
      ||  document.createElement('p');
    // grouped inputs like radios have legends; single inputs just have labels
    const fieldsetLabel = parent.getElementsByTagName('legend')[0] || parent.getElementsByTagName('label')[0];

    if (options.showErrorMsg) {
      if (!node.validity.valid && node.validationMessage) {
        errorContainer.className = INVALID_MESSAGE_CLASS;
        errorContainer.textContent = node.validationMessage;
        parent.insertBefore(errorContainer, fieldsetLabel);
        parent.classList.add(INVALID_PARENT_CLASS);
      }
    } else {
      parent.classList.remove(INVALID_PARENT_CLASS);
      errorContainer.remove();
    }
  }
}

function toggleCombinedErrorMsg(options, node) {
  const parent = findParentNode(node);
  if (parent) {
    const errorContainer = parent.querySelector(`.${INVALID_MESSAGE_CLASS}`)
      ||  document.createElement('p');
    // grouped inputs like radios have legends; single inputs just have labels
    const fieldsetLabel = parent.getElementsByTagName('legend')[0] || parent.getElementsByTagName('label')[0];
    if (options.showErrorMsg) {
      errorContainer.className = INVALID_MESSAGE_CLASS;
      errorContainer.textContent = options.errorMsg;
      parent.insertBefore(errorContainer, fieldsetLabel);
      parent.classList.add(INVALID_PARENT_CLASS);
    } else {
      parent.classList.remove(INVALID_PARENT_CLASS);
      errorContainer.remove();
    }
  }
}

function checkInputs(inputs) {
  inputs.singleInputs.forEach(function(input) {
    // prevent showing the HTML5 tooltip
    input.addEventListener('invalid', function (e) {
      e.preventDefault();
    });

    // Set a custom message if the input is invalid.
    // Note that this overrides HTML5's built-in checkValidity() function,
    // which is why it's within the forEach scope -- we don't want to override
    // the master form's checkValidity() call.
    function checkValidity() {
      const message = input.validity.valid
        ? null
        : getCustomMessage(input.type, input.validity);

      input.setCustomValidity(message || '');
    }

    input.checkValidity()
      ? toggleErrorMsg({showErrorMsg: false}, input)
      : toggleErrorMsg({showErrorMsg: true}, input);
  });

  inputs.combinedInputs.forEach(function(inputSet) {
    let groupIsValid = true;
    let errorMsg = null;

    inputSet.forEach(function(input) {
      function checkValidity() {
        const message = input.validity.valid
          ? null
          : getCustomMessage(input.type, input.validity);

        input.setCustomValidity(message || '');
      }

      if (input.checkValidity() == false) {
        groupIsValid = false;
        errorMsg = input.validationMessage;
      }
    });

    groupIsValid
      ? toggleCombinedErrorMsg({showErrorMsg: false, errorMsg: errorMsg}, inputSet[0])
      : toggleCombinedErrorMsg({showErrorMsg: true, errorMsg: errorMsg}, inputSet[0]);
  });
}

function getCombinedInputs(inputWrapper){
  return inputWrapper.querySelectorAll('input');
}

function parseInputs(inputs){
  const singleInputs = Array.from(inputs).filter(input => input.type != 'hidden' && !input.classList.contains('usa-input-inline'));
  // Dates must be validated as a set of inputs, otherwise one valid date part
  // will remove the message for the whole thing even though the set is not valid
  // (i.e., having a year but no month or day will be invalid, but will have no error message)
  const combinedInputs = Array.from(document.querySelectorAll('uswds-date')).map(uswdsDate => getCombinedInputs(uswdsDate));
  return {
    combinedInputs: combinedInputs,
    singleInputs: singleInputs
  }
}

window.addEventListener('DOMContentLoaded', () => {
  // there are several forms on the page; get the one within the .content div
  // TODO: make this a more reliable ID selector or something
  const form = document.getElementsByTagName('form')[0];
  const inputs = parseInputs(document.querySelectorAll('input, select, textarea'));
  const submitButton = document.querySelector('.submit-group button[type="submit"]');

  submitButton.addEventListener('click', function() {
    let isValid = form.checkValidity();
    if (isValid) {
      form.submit();
    } else {
      // if the form is invalid, loop through the elements to discover which need invalid messages.
      // check each valid element to make sure it doesn't have an error message displayed.
      checkInputs(inputs);
    }
  });
});
