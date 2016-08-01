/* global jQuery, document */

const $ = jQuery;
const sortableTables = document.querySelectorAll('.table-sortable');

function sortInts(intCol) {
  $(intCol).data('sortBy', (th, td) => parseInt(td.text(), 10));
}

function sortFloats(floatCol) {
  $(floatCol).data('sortBy', (th, td) => parseFloat(td.text()));
}

$(document).ready(() => {
  for (const table of sortableTables) {
    $(table).tablesort();

    // Floats should be sorted as numbers, not strings
    [].forEach.call(table.getElementsByClassName('js-float'), function sort() {
      sortFloats(this);
    });

    // Don't sort ints as strings, either
    [].forEach.call(table.getElementsByClassName('js-int'), function sort() {
      sortInts(this);
    });

    // Sort by default column, if present
    [].forEach.call(table.getElementsByClassName('js-default-sort'), () => {
      $(table).data('tablesort').sort($('.js-default-sort'));
    });
  }
});
