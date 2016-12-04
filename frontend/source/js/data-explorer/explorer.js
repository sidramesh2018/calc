/* global $, window, document, history,
  d3, formdb, wNumb  */

// wNumb is from nouislider

/**
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 *
 * Rudimentary pushstate/popstate support is implemented, but lots
 * of stuff still needs to be fixed:
 *
 *   * `.filter_active` on inputs needs to update properly.
 *   * We should probably remove hourglass.qs.parse and
 *     hourglass.qs.format.
 *   * Make sure this works on IE11, at least.
 *
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 */

import { createStore, applyMiddleware } from 'redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  HISTOGRAM_BINS,
} from './constants';

import hourglass from '../common/hourglass';

import ga from '../common/ga';

import createTable from './table';

import {
  startRatesRequest,
  completeRatesRequest,
  resetState,
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
    storeWatcher.middleware,
    formSynchronizer.reflectToFormMiddleware,
    ratesRequester.middleware,
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

  let data = ratesRequester.getRatesParameters(store);
  data = Object.assign(data, {
    experience_range: `${data.min_experience},${data.max_experience}`,
  });

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
}

function initialize() {
  table.initialize(store);

  initializeAutocomplete(store, api, $('#labor_category'));

  inputs.on('change', () => {
    formSynchronizer.reflectToStore(store);
  });

  historySynchronizer.initialize(store, () => {
    ga('set', 'page', window.location.pathname +
                      window.location.search);
    ga('send', 'pageview');
  });

  ratesRequester.initialize(store, () => {
    submit();
  });
}

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

$('.filter.contract-year .tooltip').tooltipster({
  functionInit() {
    return $(this).attr('aria-label');
  },
});

$('.slider').noUiSlider({
  start: [
    store.getState().min_experience,
    store.getState().max_experience,
  ],
  step: 1,
  connect: true,
  range: {
    min: MIN_EXPERIENCE,
    max: MAX_EXPERIENCE,
  },
});

function onExperienceChange() {
  const state = store.getState();
  const min = state.min_experience;
  const max = state.max_experience;

  $('.slider').val([min, max]);
}

storeWatcher.watch('min_experience', onExperienceChange);

storeWatcher.watch('max_experience', onExperienceChange);

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
  },
});

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
   d3.event.preventDefault();
   store.dispatch(resetState());
 });

initialize();

initReactApp({
  store,
  restoreExcludedRoot: $('#restore-excluded')[0],
  descriptionRoot: $('#description')[0],
  highlightsRoot: $('#highlights')[0],
  histogramRoot,
  proposedPriceRoot: $('#proposed-price')[0],
  educationLevelRoot: $('#education-level')[0],
});
