/* global $, window, document, d3 */

/**
 * TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
 *
 * This code was originally jQuery-based and is gradually being
 * migrated to React + Redux.
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

import App from './components/app';

import hourglass from '../common/hourglass';

import ga from '../common/ga';

import { invalidateRates } from './actions';

import appReducer from './reducers';

import StoreHistorySynchronizer from './history';

import loggingMiddleware from './logging-middleware';

import StoreRatesAutoRequester from './rates-request';

const api = new hourglass.API();
const historySynchronizer = new StoreHistorySynchronizer(window);
const ratesRequester = new StoreRatesAutoRequester(api);
const store = createStore(
  appReducer,
  applyMiddleware(
    loggingMiddleware,
    ratesRequester.middleware,
    historySynchronizer.reflectToHistoryMiddleware
  )
);

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

historySynchronizer.initialize(store, () => {
  ga('set', 'page', window.location.pathname +
                    window.location.search);
  ga('send', 'pageview');
});

store.dispatch(invalidateRates());

ReactDOM.render(
  React.createElement(
    Provider,
    { store },
    React.createElement(App, { api })
  ),
  $('[data-embed-jsx-app-here]')[0]
);
