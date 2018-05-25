/* global jQuery, document */

window.addEventListener('DOMContentLoaded', () => {
  const steps = document.querySelectorAll('.step-bar__bubbles li');
  const stepLabels = document.querySelectorAll('.step-bar__labels li');
  const currentStep = document.querySelector('.step-bar__labels .current');

  const hidePrevLabel = () => {
    const prevLabel = document.querySelector('.step-bar__labels .js-show');
    prevLabel.classList.remove('js-show');
  };

  const showLabel = (selectedLabel) => {
    hidePrevLabel();
    selectedLabel.classList.add('js-show');
  };

  for (let i = 0; i < steps.length; i++) {
    // find the step label with the same index as the hovered-over step bubble
    steps[i].addEventListener('mouseenter', () => {
      if (!stepLabels[i].classList.contains('js-show')) {
        showLabel(stepLabels[i]);
      }
    });
    // set the label back to that of the current step
    steps[i].addEventListener('mouseleave', () => {
      showLabel(currentStep);
    });
  }
});
