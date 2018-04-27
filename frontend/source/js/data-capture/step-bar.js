/* global jQuery, document */

const $ = jQuery;

$(document).ready(() => {
  const steps = $('.steps li');

  const showLabel = () => {
    //find the step label with the same index and show it; hide all others
    //show current on unhover
    
  };

  for (let i = 0; i < steps.length; i++){
    steps[i].addEventListener('mouseover', () => {
      console.log(steps[i]);
    });
  }
});
