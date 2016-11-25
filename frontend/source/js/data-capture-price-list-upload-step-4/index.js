/* global jQuery */

const $ = jQuery;
const editBtn = $('[data-edit-btn]');
const contractDetails = $('[data-contract-details]');
const editContractDetails = $('[data-edit-contract-details]');

if (editBtn.length && contractDetails.length &&
    editContractDetails.length) {
  editBtn.click(e => {
    contractDetails.slideUp();
    editContractDetails.slideDown();
    $('[data-edit-text]').each((_, el) => {
      $(el).text($(el).attr('data-edit-text'));
    });
    e.preventDefault();
  });
} else {
  throw new Error(
    'Warning! Couldn\'t find edit button and/or related elements, ' +
    'falling back to baseline behavior.'
  );
}
