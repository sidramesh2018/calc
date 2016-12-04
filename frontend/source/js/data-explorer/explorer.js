/* global $, window, document, history,
  d3, formdb, wNumb  */

// wNumb is from nouislider

/**
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 *
 * Rudimentary pushstate/popstate support is implemented, but lots
 * of stuff still needs to be fixed:
 *
 *   * Slider values need to update properly.
 *   * GA needs to be notified on navigation.
 *   * We should probably remove hourglass.qs.parse.
 *   * Make sure this works on IE11, at least.
 *
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 */

import { createStore, applyMiddleware } from 'redux';

import {
  MAX_EXPERIENCE,
  HISTOGRAM_BINS,
} from './constants';

// import ga from '../common/ga';

import hourglass from '../common/hourglass';

/*
import {
  location,
  getUrlParameterByName,
} from './util';
*/

import createTable from './table';

import {
  startRatesRequest,
  completeRatesRequest,
} from './actions';

import appReducer from './reducers';

import histogramToImg from './histogram-to-img';

import initializeAutocomplete from './autocomplete';

import {
  StoreFormSynchronizer,
  StoreHistorySynchronizer,
  StoreRatesAutoRequester,
  StoreStateFieldWatcher,
} from './store-form-synchronizer';

import initReactApp from './app';

const search = d3.select('#search');
const form = new formdb.Form(search.node());
const formSynchronizer = new StoreFormSynchronizer(form);
const historySynchronizer = new StoreHistorySynchronizer(window);
const ratesRequester = new StoreRatesAutoRequester();
const storeWatcher = new StoreStateFieldWatcher();
const store = createStore(
  appReducer,
  applyMiddleware(
    formSynchronizer.reflectToFormMiddleware,
    ratesRequester.middleware,
    storeWatcher.middleware,
    historySynchronizer.reflectToHistoryMiddleware
  )
);
const inputs = search.selectAll('*[name]');
const api = new hourglass.API();
const loadingIndicator = search.select('.loading-indicator');
const histogramRoot = document.getElementById('price-histogram');
const histogramDownloadLink = document.getElementById('download-histogram');
const table = createTable('#results-table');

let request;

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

  table.updateResults();
}

storeWatcher.watch('contract-year', () => {
  table.updateResults();
});

function submit() {
  table.updateSort();

  const data = ratesRequester.getRatesParameters(store);

  inputs
    .filter(function filter() {
      return this.type !== 'radio' && this.type !== 'checkbox';
    })
    .classed('filter_active', function classed() {
      return !!this.value;
    });

  search.classed('loaded', false);
  search.classed('loading', true);

  // cancel the outbound request if there is one
  if (request) request.abort();
  const defaults = {
    histogram: HISTOGRAM_BINS,
    experience_range: `${data.min_experience},${data.max_experience}`,
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

/*
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
*/
}

/*
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

  submit(false);
}
*/

function initialize() {
  table.initialize(store);

//  popstate();

  initializeAutocomplete(store, api, $('#labor_category'));

  inputs.on('change', () => {
    formSynchronizer.reflectToStore(store);
  });

  historySynchronizer.initialize(store);

  ratesRequester.initialize(store, () => {
    submit();
  });
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
$('.filter.contract-year .tooltip').tooltipster({
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

/*
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
*/

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

    formSynchronizer.reflectToStore(store);

    if ($('#min_experience').val() === '0' && $('#max_experience').val() === `${MAX_EXPERIENCE}`) {
      $('#min_experience, #max_experience').removeClass('filter_active');
    }
  },
});

// on load remove active class on experience slider
$('#min_experience, #max_experience').removeClass('filter_active');

/*
// load experience range if query string exists
if (getUrlParameterByName('max_experience').length) {
  $('.slider').val([getUrlParameterByName('min_experience'),
    getUrlParameterByName('max_experience')]);
}
*/

// window.addEventListener('popstate', popstate);

histogramDownloadLink.addEventListener('click', e => {
  e.preventDefault();
  histogramToImg(
    // TODO: We're reaching into a React component here, which isn't
    // a great idea. This should get cleaner once we make the download
    // link a React component too.
    $(histogramRoot).find('svg')[0],
    document.getElementById('graph')
  );
}, false);

form.on('submit', (data, e) => {
  e.preventDefault();
  formSynchronizer.reflectToStore(store);
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

   d3.event.preventDefault();

   $('.multiSel').empty();
   $('.eduSelect').show();
   if ($('.multiSelect input:checked').length) {
     $('.multiSelect input:checked').attr('checked', false);
   }
   $('.slider').val([0, MAX_EXPERIENCE]);

   formSynchronizer.reflectToStore(store);
 });

initReactApp({
  store,
  restoreExcludedRoot: $('#restore-excluded')[0],
  descriptionRoot: $('#description')[0],
  highlightsRoot: $('#highlights')[0],
  histogramRoot,
  proposedPriceRoot: $('#proposed-price')[0],
});
