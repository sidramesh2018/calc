import {
  startRatesRequest,
  completeRatesRequest,
} from './actions';

import {
  HISTOGRAM_BINS,
} from './constants';

import {
  autobind,
} from './util';

import {
  allFields,
  getSerializedFields,
} from './serialization';

const nonRatesFields = ['proposed-price', 'contract-year'];

const ratesFields = allFields.filter(f => nonRatesFields.indexOf(f) === -1);

export default class StoreRatesAutoRequester {
  constructor(api) {
    this.api = api;
    this.request = null;
    autobind(this, ['middleware']);
  }

  getRatesParameters(store) {
    const data = getSerializedFields(store.getState(), ratesFields, {
      omitEmpty: true,
    });
    return Object.assign(data, {
      experience_range: `${data.min_experience},${data.max_experience}`,
    });
  }

  _startRatesRequest(store) {
    if (this.request) {
      this.request.abort();
    }

    const data = this.getRatesParameters(store);
    const defaults = {
      histogram: HISTOGRAM_BINS,
    };

    store.dispatch(startRatesRequest());

    this.request = this.api.get({
      uri: 'rates/',
      data: Object.assign(defaults, data),
    }, (error, res) => {
      this.request = null;

      store.dispatch(completeRatesRequest(error, res));
    });
  }

  middleware(store) {
    return next => action => {
      const oldState = store.getState();
      const result = next(action);
      const newState = store.getState();
      const updated = ratesFields.some(
        field => newState[field] !== oldState[field]
      );

      if (updated || newState.rates.stale) {
        this._startRatesRequest(store);
      }

      return result;
    };
  }
}
