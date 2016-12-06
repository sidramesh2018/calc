import {
  invalidateRates,
} from './actions';

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
  constructor() {
    autobind(this, ['middleware']);
  }

  initialize(store, onRatesRequest) {
    Object.assign(this, {
      onRatesRequest,
    });

    store.dispatch(invalidateRates());
  }

  getRatesParameters(store) {
    return getSerializedFields(store.getState(), ratesFields, {
      omitEmpty: true,
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
        if (this.onRatesRequest) {
          this.onRatesRequest(store);
        }
      }

      return result;
    };
  }
}
