/* global $, window, document, history,
  d3, formdb, wNumb  */

// wNumb is from nouislider

import { createStore, applyMiddleware } from 'redux';

import {
  MAX_EXPERIENCE,
  HISTOGRAM_BINS,
  EMPTY_RATES_DATA,
} from './constants';

import ga from '../common/ga';

import hourglass from '../common/hourglass';

import {
  location,
  getUrlParameterByName,
  arrayToCSV,
  formatCommas,
  isNumberOrPeriodKey,
} from './util';

import {
  updateResults,
  updateSort,
  initializeTable,
} from './table';

import {
  startRatesRequest,
  completeRatesRequest,
} from './actions';

import appReducer from './reducers';

import updatePriceHistogram from './histogram';

import histogramToImg from './histogram-to-img';

import initializeAutocomplete from './autocomplete';

import StoreFormSynchronizer from './store-form-synchronizer';

import initReactApp from './app';

const search = d3.select('#search');
const form = new formdb.Form(search.node());
const synchronizer = new StoreFormSynchronizer(form);
const store = createStore(
  appReducer,
  applyMiddleware(synchronizer.reflectToFormMiddleware)
);
const inputs = search.selectAll('*[name]');
const api = new hourglass.API();
const loadingIndicator = search.select('.loading-indicator');
const histogramDownloadLink = document.getElementById('download-histogram');

let request;
let updateCounter = 0;

function updateDescription(res) {
  const data = form.getData();
  const filters = $('.filters');
  const laborCategoryValue = $('#labor_category').val();
  const lookup = {
    education: {
      label: 'education level',
      html: $('.multiSel').html(),
    },
    min_experience: {
      label: 'experience',
      html: `${$('#min_experience option:selected').text()} - ` +
            `${$('#max_experience option:selected').text()} years`,
    },
    site: {
      label: 'worksite',
      html: $('.filter-site option:selected').text(),
    },
    business_size: {
      label: 'business size',
      html: $('.filter-business_size option:selected').text(),
    },
    schedule: {
      label: 'schedule',
      html: $('.filter-schedule option:selected').text(),
    },
  };

  if (updateCounter) {
    filters.empty().removeClass('hidden').append('with ');
  }

  // fade effect for transitions during description update
  $('#description').hide().fadeIn();

  // first count of results
  d3.select('#description-count')
    .text(formatCommas(res.results.length));

  // labor category results
  if (laborCategoryValue) {
    const laborEl = $(document.createElement('span')).addClass('filter');
    filters.append(laborEl);
    laborEl.append(
      $(document.createElement('a')).addClass('focus-input').attr('href', '#')
        .html(laborCategoryValue)
    );
  }

  Object.keys(data).forEach((dataKey) => {
    if (lookup[dataKey]) {
      // create a span element filter label
      const filterEl = $(document.createElement('span'))
          .addClass(`filter ${dataKey}-filter`)
          .html(` ${lookup[dataKey].label}: `);

      filters.append(filterEl);

      // append text of selected filter as anchor elements
      filterEl.append(
        $(document.createElement('a')).addClass('focus-input')
          .attr('href', '#')
          .html(lookup[dataKey].html)
      );
    }
  });
}

function update(error, res) {
  search.classed('loading', false);
  request = null;

  if (error) {
    if (error === 'abort') {
      // ignore aborts
      return;
    }

    search.classed('error', true);

    loadingIndicator.select('.error-message')
      .text(error);
  } else {
    search.classed('error', false);
  }

  search.classed('loaded', true);

  store.dispatch(completeRatesRequest(error, res));

  updateDescription(res);
  updateCounter++;

  if ($('.proposed-price input').val()) {
    res.proposedPrice = $('.proposed-price input').val(); // eslint-disable-line no-param-reassign
    $('.proposed-price-highlight').html(`$${$('.proposed-price input').val()}`);
    $('.proposed-price-block').fadeIn();
  } else {
    res.proposedPrice = 0; // eslint-disable-line no-param-reassign
    $('.proposed-price-block').fadeOut();
  }

  if (res && res.results && res.results.length) {
    updatePriceHistogram(res);
    updateResults(store, form, res);
  } else {
    res = EMPTY_RATES_DATA; // eslint-disable-line no-param-reassign
    // updatePriceRange(EMPTY_DATA);
    updatePriceHistogram(res);
    updateResults(store, form, res);
  }
}

function submit(pushState) {
  let data = form.getData();

  data = arrayToCSV(data);

  inputs
    .filter(function filter() {
      return this.type !== 'radio' && this.type !== 'checkbox';
    })
    .classed('filter_active', function classed() {
      return !!this.value;
    });

  data.experience_range = `${$('#min_experience').val()},${$('#max_experience').val()}`;

  search.classed('loaded', false);
  search.classed('loading', true);

  // cancel the outbound request if there is one
  if (request) request.abort();
  const defaults = {
    histogram: HISTOGRAM_BINS,
  };

  store.dispatch(startRatesRequest());

  request = api.get({
    uri: 'rates/',
    data: hourglass.extend(defaults, data),
  }, update);


  d3.select('#export-data')
    .attr('href', function updateQueryString() {
      return [
        this.href.split('?').shift(),
        hourglass.qs.format(data),
      ].join('?');
    });

  if (pushState) {
    const href = `?${hourglass.qs.format(data)}`;
    const didSearchChange = window.location.search !== href;

    history.pushState(null, null, href);

    if (didSearchChange) {
      ga('set', 'page', window.location.pathname +
                        window.location.search);
      ga('send', 'pageview');
    }
  }

  synchronizer.reflectToStore(store);
}

synchronizer.setSubmitForm(submit);

function popstate() {
  // read the query string and set values accordingly
  const data = hourglass.extend(
    form.getData(),
    hourglass.qs.parse(location.search)
  );
  inputs.on('change', null);
  form.setData(data);
  inputs.on('change', () => {
    submit(true);
  });

  updateSort(data.sort);

  submit(false);
}

function initialize() {
  initializeTable(form, submit);

  popstate();

  initializeAutocomplete(form, api, $('#labor_category'));
}

/*
  Dropdown with Multiple checkbox select with jQuery - May 27, 2013
  (c) 2013 @ElmahdiMahmoud
  license: http://www.opensource.org/licenses/mit-license.php
  // many edits by xtine
*/
$('.dropdown dt a').on('click', (e) => {
  $('.dropdown dd ul').slideToggle('fast');

  e.preventDefault();
});

$('.dropdown dd ul li a').on('click', (e) => {
  $('.dropdown dd ul').hide();

  e.preventDefault();
});

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

// initialize tooltipster.js
$('.tooltip').tooltipster({
  functionInit() {
    return $(this).attr('aria-label');
  },
});

initialize();

$(document).bind('click', (e) => {
  const $clicked = $(e.target);
  if (!$clicked.parents().hasClass('dropdown')) $('.dropdown dd ul').hide();
});


$('.multiSelect input[type="checkbox"]').on('click', function onClick() {
  const title = $(this).next().html();

  if ($(this).is(':checked')) {
    const html = `<span title="${title}">${title}</span>`;

    $('.multiSel').append(html);
    $('.eduSelect').hide();
  } else {
    $(`span[title="${title}"]`).remove();
    $('.dropdown dt a').addClass('hide');
  }

  if (!$('.multiSelect input:checked').length) {
    $('.eduSelect').show();
  } else {
    $('.eduSelect').hide();
  }
});

if (getUrlParameterByName('education').length) {
  const parameters = getUrlParameterByName('education').split(',');

  $('.eduSelect').hide();

  parameters.forEach((param) => {
    const title = $(`.multiSelect input[type=checkbox][value=${param}]`)
      .attr('checked', true)
      .next()
      .html();

    $('.multiSel').append(`<span title="${title}">${title}</span>`);
  });
}

$('.slider').noUiSlider({
  start: [0, MAX_EXPERIENCE],
  step: 1,
  connect: true,
  range: {
    min: 0,
    max: MAX_EXPERIENCE,
  },
});

$('.slider').Link('lower').to($('#min_experience'), null, wNumb({ // eslint-disable-line new-cap
  decimals: 0,
}));
$('.slider').Link('upper').to($('#max_experience'), null, wNumb({ // eslint-disable-line new-cap
  decimals: 0,
}));

$('.slider').on({
  slide() {
    $('.noUi-horizontal .noUi-handle').addClass('filter_focus');
  },
  set() {
    $('.noUi-horizontal .noUi-handle').removeClass('filter_focus');

    submit(true);

    if ($('#min_experience').val() === '0' && $('#max_experience').val() === `${MAX_EXPERIENCE}`) {
      $('#min_experience, #max_experience').removeClass('filter_active');
    }
  },
});

// on load remove active class on experience slider
$('#min_experience, #max_experience').removeClass('filter_active');

// load experience range if query string exists
if (getUrlParameterByName('max_experience').length) {
  $('.slider').val([getUrlParameterByName('min_experience'),
    getUrlParameterByName('max_experience')]);
}

// restrict proposed price input to be numeric only
$('.proposed-price input').keypress((e) => {
  if (!isNumberOrPeriodKey(e)) {
    e.preventDefault();
  }
});

// trigger proposed button input
$('.proposed-price button').click(() => {
  if ($('.proposed-price input').val()) {
    $('.proposed-price-highlight').html(`$${$('.proposed-price input').val()}`);

    $('.proposed-price-block').fadeIn();
  } else {
    $('.proposed-price-block').fadeOut();
  }
});


if (getUrlParameterByName('proposed-price').length) {
  $('.proposed-price-highlight').html(`$${getUrlParameterByName('proposed-price')}`);
  $('.proposed-price-block').show();
}

$(document).keypress((e) => {
  // NOTE: JAS: Seems weird to apply this to the entire document
  if (e.which === 13) {
    $('.proposed-price button').trigger('click');
  }
});

$('.two-decimal-places').keyup(function onKeyUp() {
  // regex checks if there are more than 2 numbers after decimal point
  if (!(/^\d+(\.{0,1}\d{0,2})?$/.test(this.value))) {
    // cut off and prevent user from inputting more than 2 numbers after decimal place
    this.value = this.value.substring(0, this.value.length - 1);
  }
});

window.addEventListener('popstate', popstate);

histogramDownloadLink.addEventListener('click', e => {
  e.preventDefault();
  histogramToImg(
    document.getElementById('price-histogram'),
    document.getElementById('graph')
  );
}, false);

form.on('submit', (data, e) => {
  e.preventDefault();
  submit(true);
});

/*
* For some reason, the browser's native form reset isn't working.
* So instead of just listening for a "reset" event and submitting,
* we hijack the click event on the reset button and reset the form
* manually.
*/
search.select('input[type="reset"]')
 .on('click', () => {
   form.reset();
   // NB: form.reset() doesn't reset hidden inputs,
   // so we need to do it ourselves.
   search.selectAll('input[type="hidden"]')
     .property('value', '');

   submit(true);
   d3.event.preventDefault();

   $('.multiSel').empty();
   $('.eduSelect').show();
   if ($('.multiSelect input:checked').length) {
     $('.multiSelect input:checked').attr('checked', false);
   }
   $('.slider').val([0, 45]);
 });

inputs.on('change', () => {
  submit(true);
});

initReactApp({
  store,
  restoreExcludedRoot: $('#restore-excluded')[0],
});
