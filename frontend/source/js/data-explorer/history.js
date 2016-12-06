import {
  setState,
} from './actions';

import {
  autobind,
} from './util';

import {
  allFields,
  serializers,
  deserializers,
  getChangedSerializedFields,
} from './serialization';

// http://stackoverflow.com/a/13419367
function parseQuery(qstr) {
  const query = {};
  const a = qstr.substr(1).split('&');

  for (let i = 0; i < a.length; i++) {
    const b = a[i].split('=');
    query[decodeURIComponent(b[0])] = decodeURIComponent(b[1] || '');
  }

  return query;
}

function joinQuery(query) {
  const parts = Object.keys(query).map(name => {
    const encName = encodeURIComponent(name);
    const encValue = encodeURIComponent(query[name]);

    return `${encName}=${encValue}`;
  }).join('&');

  return `?${parts}`;
}

export default class StoreHistorySynchronizer {
  constructor(window) {
    autobind(this, ['reflectToHistoryMiddleware']);

    this.window = window;
    this.isReflectingToStore = false;
    this.onLoctionChanged = () => {};
  }

  initialize(store, onLocationChanged) {
    this.onLocationChanged = onLocationChanged;
    this.window.addEventListener('popstate', () => {
      this.reflectToStore(store);
      this.onLocationChanged();
    });
    this.reflectToStore(store);
  }

  reflectToStore(store) {
    const qsFields = parseQuery(this.window.location.search);
    const state = store.getState();
    const changes = {};

    allFields.forEach(field => {
      const oldVal = serializers[field](state[field]);
      const newDeserializedVal = deserializers[field](qsFields[field]);
      const newVal = serializers[field](newDeserializedVal);

      if (oldVal !== newVal) {
        changes[field] = newDeserializedVal;
      }
    });

    if (Object.keys(changes).length) {
      this.isReflectingToStore = true;
      store.dispatch(setState(Object.assign({}, state, changes)));
      this.isReflectingToStore = false;
    }
  }

  reflectToHistoryMiddleware(store) {
    const defaultState = store.getState();

    return next => action => {
      const oldState = store.getState();
      const result = next(action);
      const newState = store.getState();
      const changed = allFields.some(
        field => newState[field] !== oldState[field]
      );

      if (changed && !this.isReflectingToStore) {
        const nonDefaultFields = getChangedSerializedFields(
          defaultState,
          newState,
          allFields
        );

        const qs = joinQuery(nonDefaultFields);

        this.window.history.pushState(null, null, qs);
        this.onLocationChanged();
      }

      return result;
    };
  }
}
