/* global window, document */

import 'document-register-element';

import * as supports from './feature-detection';

import { dispatchBubbly } from './custom-event';

const KEY_SPACE = 32;
const KEY_ENTER = 13;

/**
 * CollapsibleArea represents a <collapsible-area> web component.
 */

class CollapsibleArea extends window.HTMLElement {
  attachedCallback() {
    if ('isUpgraded' in this) {
      // We've already been attached.
      return;
    }

    this.expander = this.firstElementChild;

    this.isUpgraded = Boolean(this.expander &&
                              !supports.isForciblyDegraded(this));

    if (this.isUpgraded) {
      this.expander.setAttribute('aria-expanded', 'false');
      this.expander.setAttribute('role', 'button');
      this.expander.setAttribute('tabindex', '0');
      this.expander.addEventListener('click', this.toggle.bind(this), false);
      this.expander.addEventListener('keyup', e => {
        if (e.keyCode === KEY_SPACE || e.keyCode === KEY_ENTER) {
          this.toggle();
        }
      }, true);
      dispatchBubbly(this, 'collapsibleareaready');
    }
  }

  toggle() {
    if (!this.isUpgraded) {
      return;
    }

    const newVal = this.expander.getAttribute('aria-expanded') === 'true'
                   ? 'false' : 'true';
    this.expander.setAttribute('aria-expanded', newVal);
  }
}

CollapsibleArea.prototype.SOURCE_FILENAME = __filename;

document.registerElement('collapsible-area', {
  prototype: CollapsibleArea.prototype,
});

module.exports = CollapsibleArea;
