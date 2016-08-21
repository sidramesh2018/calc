/* global jQuery, document, window */

import 'document-register-element';

import * as supports from './feature-detection';

const $ = jQuery;

const MISC_ERROR = 'Sorry, we’re having trouble. ' +
                   'Please try again later or refresh your browser.';

let delegate = {
  redirect(url) {
    window.location = url;
  },
  alert(msg) {
    // TODO: Be more user-friendly here.
    window.alert(msg);   // eslint-disable-line no-alert
  },
};

function replaceForm(form, html) {
  const newForm = $(html)[0];

  // Replace the form and bind it.
  $(form).replaceWith(newForm);

  // Animate the new form so the user notices it.
  // TODO: Consider using a CSS class w/ a transition or animation instead.
  $(newForm).hide().fadeIn();
}

function bindForm(form) {
  const self = { form };

  // This is mostly just for test suites to use.
  $(form).data('ajaxform', self);

  $(form).on('submit', (e) => {
    if (!supports.formData()) {
      // Assume the browser has
      // minimal HTML5 support and just let the user submit the form manually.
    } else {
      e.preventDefault();

      const formData = new window.FormData();

      // IE11 doesn't support FormData.prototype.delete(), so we need to
      // manually construct the FormData ourselves (we used to have
      // the browser construct it for us, and then replace the file).
      for (let i = 0; i < form.elements.length; i++) {
        const el = form.elements[i];

        if (el.isUpgraded) {
          formData.append(el.name, el.upgradedValue);
        } else {
          const elType = el.getAttribute('type');

          if (elType === 'radio' || elType === 'checked') {
            // https://github.com/18F/calc/issues/570
            throw new Error(`unsupported input type: ${elType}`);
          } else if (elType === 'file') {
            for (let j = 0; j < el.files.length; j++) {
              formData.append(el.name, el.files[j]);
            }
          } else {
            formData.append(el.name, el.value);
          }
        }
      }

      const req = $.ajax(form.action, {
        processData: false,
        contentType: false,
        data: formData,
        method: form.method,
      });

      $(form).addClass('submit-in-progress');

      req.done((data) => {
        if (data.form_html) {
          replaceForm(form, data.form_html);
        } else if (data.redirect_url) {
          delegate.redirect(data.redirect_url);
        } else {
          delegate.alert(MISC_ERROR);
          $(form).removeClass('submit-in-progress');
        }
      });

      req.fail(() => {
        delegate.alert(MISC_ERROR);
        $(form).removeClass('submit-in-progress');
      });
    }
  });

  return self;
}

exports.setDelegate = newDelegate => {
  delegate = newDelegate;
  return delegate;
};
exports.MISC_ERROR = MISC_ERROR;
exports.bindForm = bindForm;

window.testingExports__ajaxform = exports;

class AjaxForm extends window.HTMLFormElement {
  createdCallback() {
    bindForm(this);
  }
}

document.registerElement('ajax-form', {
  extends: 'form',
  prototype: AjaxForm.prototype,
});
