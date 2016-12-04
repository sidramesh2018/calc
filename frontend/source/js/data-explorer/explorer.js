/* global $, window, document, history,
  d3, formdb, wNumb  */

// wNumb is from nouislider

/**
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 *
 * Rudimentary pushstate/popstate support is implemented, but lots
 * of stuff still needs to be fixed:
 *
 *   * Education checkboxes aren't updated properly if multiple
 *     checkboxes are checked.
 *   * `.filter_active` on inputs needs to update properly.
 *   * GA needs to be notified on navigation, e.g.:
 *
 *       import ga from '../common/ga';
 *       ga('set', 'page', window.location.pathname +
 *                         window.location.search);
 *       ga('send', 'pageview');
 *
 *   * We should probably remove hourglass.qs.parse.
 *   * Make sure this works on IE11, at least.
 *
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 */

import { createStore, applyMiddleware } from 'redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  HISTOGRAM_BINS,
  EDU_LABELS,
} from './constants';

import hourglass from '../common/hourglass';

import createTable from './table';

import {
  startRatesRequest,
  completeRatesRequest,
  setState,
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
const defaultState = store.getState();
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
}

function initialize() {
  table.initialize(store);

  initializeAutocomplete(store, api, $('#labor_category'));

  inputs.on('change', () => {
    formSynchronizer.reflectToStore(store);
  });

  historySynchronizer.initialize(store);

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

// Whenever users click outside of our dropdown, hide it.
$(document).bind('click', (e) => {
  const $clicked = $(e.target);
  if (!$clicked.parents().hasClass('dropdown')) $('.dropdown dd ul').hide();
});

storeWatcher.watch('education', () => {
  const education = store.getState().education;
  const instructions = $('.eduSelect');
  const filterList = $('.multiSel');

  instructions.toggle(education.length === 0);
  filterList.empty();

  education.forEach(ed => {
    const item = $('<span></span>');
    const label = EDU_LABELS[ed];
    item.attr('title', label);
    item.text(label);
    filterList.append(item);
  });
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
   store.dispatch(setState(defaultState));
 });

initialize();

initReactApp({
  store,
  restoreExcludedRoot: $('#restore-excluded')[0],
  descriptionRoot: $('#description')[0],
  highlightsRoot: $('#highlights')[0],
  histogramRoot,
  proposedPriceRoot: $('#proposed-price')[0],
});
