/* global window, document */
import 'document-register-element';

const STEP_CLASS = '.step-bar__bubbles li';
const STEP_LABEL_CLASS = '.step-bar__labels li';
const CURRENT_STEP_CLASS = '.step-bar__labels .current';

class StepBar extends window.HTMLElement {
  attachedCallback() {
    const steps = this.querySelectorAll(STEP_CLASS);
    const stepLabels = this.querySelectorAll(STEP_LABEL_CLASS);
    const currentStep = this.querySelector(CURRENT_STEP_CLASS);

    if (steps && stepLabels && currentStep) {
      // set it all up
      const path = this._createPath(steps);
      for (let i = 0; i < steps.length; i++) {
        // find the step label with the same index as the hovered-over step bubble
        steps[i].addEventListener('mouseenter', () => {
          if (!stepLabels[i].classList.contains('js-show')) {
            this._showLabel(stepLabels[i]);
          }
        });

        // set the label back to that of the current step
        steps[i].addEventListener('mouseleave', () => {
          this._showLabel(currentStep);
        });

        // create link for each step, starting at 1
        this._addLink(path, steps[i], i+1);
      }
    }
  }

  // Hide the label that was visible
  _hidePrevLabel() {
    const prevLabel = this.querySelector('.step-bar__labels .js-show');
    prevLabel.classList.remove('js-show');
  };

  // Show the label corresponding to the hovered-over bubble
  _showLabel(selectedLabel) {
    this._hidePrevLabel();
    selectedLabel.classList.add('js-show');
  };

  _getIndexOfClass(classname, nodes) {
    let itemIndex;
    nodes.forEach((item, i, listObj) => {
      if (item.className == classname) {
        itemIndex = i;
      }
    });
    return itemIndex;
  }

  // Create the link for each step. Ideally we would do this in the Django
  // view frontend/steps.py, but accessing URL patterns from that file creates
  // a circular import. Attempted in https://github.com/18F/calc/pull/1981
  // This code assumes the path of the page is in the form of
  // /data-capture/step/1 or data-capture/bulk/region-10/step/3,
  // i.e., the step number is at the end of the URL as per patterns in urls.py
  _createPath(steps) {
    let path = window.location.pathname;
    const currentStepNum = this._getIndexOfClass('current', steps) + 1;
    // Remove the step number from the end of the path
    const re = new RegExp(`${currentStepNum}$`);
    return path.replace(re, '');
  }

  _addLink(path, step, stepNum) {
    const emptyLink = step.getElementsByTagName('a')[0];
    const relativeUrl = path + stepNum;
    emptyLink.setAttribute('href', relativeUrl);
  }
}

document.registerElement('step-bar', {
  prototype: StepBar.prototype,
});

module.exports = StepBar;
