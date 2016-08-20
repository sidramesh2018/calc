/* global jQuery, window */

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

function browserSupportsFormData() {
  return 'FormData' in window;
}

function getForm() {
  return $('[data-ajaxform]')[0];
}

function replaceForm(html) {
  // Replace the form and bind it.
  $(getForm()).replaceWith(html);

  // Animate the new form so the user notices it.
  // TODO: Consider using a CSS class w/ a transition or animation instead.
  $(getForm()).hide().fadeIn();
}

function bindForm() {
  const form = getForm();
  const $submit = $('button[type=submit]', form);

  if (!form) {
    return null;
  }

  const self = { form, $submit };

  if (!$submit.length) {
    throw new Error('ajaxform must contain a <button type="submit">');
  }

  // This is mostly just for test suites to use.
  $(form).data('ajaxform', self);

  $(form).on('submit', (e) => {
    if (!browserSupportsFormData()) {
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

        if (typeof el.getUpgradedValue === 'function') {
          formData.append(el.name, el.getUpgradedValue());
        } else {
          const elType = el.getAttribute('type');
          if (elType === 'radio' || elType === 'checked') {
            // https://github.com/18F/calc/issues/570
            throw new Error(`unsupported input type: ${elType}`);
          }
          formData.append(el.name, el.value);
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
          replaceForm(data.form_html);
          bindForm();
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

$(bindForm);

exports.setDelegate = newDelegate => {
  delegate = newDelegate;
  return delegate;
};
exports.MISC_ERROR = MISC_ERROR;
exports.getForm = getForm;
exports.bindForm = bindForm;

window.testingExports__ajaxform = exports;
