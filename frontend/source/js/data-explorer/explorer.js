/* global $, window, document, d3 */

/**
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 *
 * This code was originally jQuery-based and is gradually being
 * migrated to React + Redux.
 *
 * To visually see what's been converted, paste the following
 * into the console:
 *
 *   $('[data-reactroot]').css({border: '1px solid green'});
 *
 * Things to be fixed include, but are not limited to:
 *
 *   * We should probably remove `hourglass.qs.parse` and
 *     `hourglass.qs.format`.
 *   * We might want to get rid of `location` in `./util`.
 *
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 */

import ReactDOM from 'react-dom';
import React from 'react';
import { createStore, applyMiddleware } from 'redux';
import { Provider } from 'react-redux';

import * as components from './components';

import hourglass from '../common/hourglass';

import ga from '../common/ga';

import {
  invalidateRates,
  resetState,
} from './actions';

import appReducer from './reducers';

import histogramToImg from './histogram-to-img';

import StoreHistorySynchronizer from './history';

import {
  StoreStateFieldWatcher,
  loggingMiddleware,
} from './temp-redux-middleware';

import StoreRatesAutoRequester from './rates-request';

const api = new hourglass.API();
const search = d3.select('#search');
const historySynchronizer = new StoreHistorySynchronizer(window);
const ratesRequester = new StoreRatesAutoRequester(api);
const storeWatcher = new StoreStateFieldWatcher();
const store = createStore(
  appReducer,
  applyMiddleware(
    loggingMiddleware,
    storeWatcher.middleware,
    ratesRequester.middleware,
    historySynchronizer.reflectToHistoryMiddleware
  )
);
const histogramDownloadLink = document.getElementById('download-histogram');

function onCompleteRatesRequest(error) {
  search.classed('loading', false);

  if (error) {
    if (error === 'abort') {
      // ignore aborts
      return;
    }

    search.classed('error', true);
  } else {
    search.classed('error', false);
  }

  search.classed('loaded', true);
}

function onStartRatesRequest() {
  search.classed('loaded', false);
  search.classed('loading', true);
}

storeWatcher.watch('rates', () => {
  const rates = store.getState().rates;

  if (!rates.stale) {
    if (rates.inProgress) {
      onStartRatesRequest();
    } else {
      onCompleteRatesRequest(rates.error);
    }
  }
});

function initialize() {
  historySynchronizer.initialize(store, () => {
    ga('set', 'page', window.location.pathname +
                      window.location.search);
    ga('send', 'pageview');
  });

  store.dispatch(invalidateRates());
}

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

histogramDownloadLink.addEventListener('click', e => {
  e.preventDefault();
  histogramToImg(
    // TODO: We're reaching into a React component here, which isn't
    // a great idea. This should get cleaner once we make the download
    // link a React component too.
    $('[data-embed-jsx="Histogram"]').find('svg')[0],
    document.getElementById('graph')
  );
}, false);

$('form').on('submit', e => {
  e.preventDefault();
  store.dispatch(invalidateRates());
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

$('[data-embed-jsx]').each(function embedJsx() {
  const rootEl = this;
  const name = this.getAttribute('data-embed-jsx');

  if (name in components) {
    ReactDOM.render(
      React.createElement(Provider, { store },
                          React.createElement(components[name], {
                            api,
                          })),
      rootEl
    );
  } else {
    throw new Error(`Unknown component: ${name}`);
  }
});
