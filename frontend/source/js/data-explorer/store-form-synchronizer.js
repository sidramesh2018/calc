import { setState } from './actions';

import {
  EDU_LABELS,
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  SITE_LABELS,
  BUSINESS_SIZE_LABELS,
  SCHEDULE_LABELS,
  CONTRACT_YEAR_LABELS,
  DEFAULT_CONTRACT_YEAR,
  DEFAULT_SORT,
  DEFAULT_QUERY_TYPE,
  QUERY_TYPE_LABELS,
} from './constants';

import {
  parsePrice,
} from './util';

const parseSort = val => {
  if (!val) {
    return DEFAULT_SORT;
  }

  // TODO: Ensure the key is valid.

  if (val.charAt(0) === '-') {
    return { key: val.substr(1), descending: true };
  }
  return { key: val, descending: false };
};

const coercedString = val => {
  if (val === undefined) {
    return '';
  }
  return String(val);
};

const coercedExperience = defaultVal => val => {
  const valInt = parseInt(val, 10);

  if (isNaN(valInt)) {
    return defaultVal;
  }

  return Math.max(Math.min(valInt, MAX_EXPERIENCE), MIN_EXPERIENCE);
};

const stringInSet = (choices, defaultVal = '') => val => {
  if (val in choices) {
    return val;
  }

  return defaultVal;
};

const serializers = {
  exclude: list => list.map(coercedString).join(','),
  education: list => list.map(coercedString).join(','),
  q: coercedString,
  'contract-year': coercedString,
  site: coercedString,
  business_size: coercedString,
  schedule: coercedString,
  min_experience: coercedString,
  max_experience: coercedString,
  'proposed-price': coercedString,
  sort: ({ key, descending }) => (descending ? '-' : '') + key,
  query_type: coercedString,
};

const deserializers = {
  exclude: list =>
    coercedString(list)
      .split(',')
      .map(x => parseInt(x, 10))
      .filter(x => !isNaN(x)),
  education: list =>
    coercedString(list)
      .split(',')
      .filter(x => x in EDU_LABELS),
  q: coercedString,
  'contract-year': stringInSet(CONTRACT_YEAR_LABELS, DEFAULT_CONTRACT_YEAR),
  site: stringInSet(SITE_LABELS),
  business_size: stringInSet(BUSINESS_SIZE_LABELS),
  schedule: stringInSet(SCHEDULE_LABELS),
  min_experience: coercedExperience(MIN_EXPERIENCE),
  max_experience: coercedExperience(MAX_EXPERIENCE),
  'proposed-price': parsePrice,
  sort: parseSort,
  query_type: stringInSet(QUERY_TYPE_LABELS, DEFAULT_QUERY_TYPE),
};

const allFields = Object.keys(serializers);

const nonRatesFields = ['proposed-price', 'contract-year'];

const ratesFields = allFields.filter(f => nonRatesFields.indexOf(f) === -1);

function getSerializedFields(state, fields, options = {}) {
  const result = {};

  fields.forEach(field => {
    const val = serializers[field](state[field]);

    if (options.omitEmpty && !val.length) {
      return;
    }

    result[field] = val;
  });

  return result;
}

function getChangedSerializedFields(oldState, newState, fields) {
  const result = {};

  fields.forEach(field => {
    const oldVal = serializers[field](oldState[field]);
    const newVal = serializers[field](newState[field]);

    if (oldVal !== newVal) {
      result[field] = newVal;
    }
  });

  return result;
}

function autobind(self, names) {
  const target = self;

  names.forEach(name => {
    target[name] = target[name].bind(target);
  });
}

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

export function StoreStateFieldWatcher() {
  const watchers = [];

  return {
    watch(name, cb) {
      watchers.push([name, cb]);
    },

    middleware(store) {
      return next => action => {
        const oldState = store.getState();
        const result = next(action);
        const newState = store.getState();

        watchers.forEach(([name, cb]) => {
          if (oldState[name] !== newState[name]) {
            cb();
          }
        });

        return result;
      };
    },
  };
}

export class StoreRatesAutoRequester {
  constructor() {
    autobind(this, ['middleware']);
  }

  initialize(store, onRatesRequest) {
    Object.assign(this, {
      onRatesRequest,
    });

    // TODO: We should make a separate action for loading rates
    // if invalid or something.
    store.dispatch(setState(Object.assign(store.getState())));
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

export class StoreHistorySynchronizer {
  constructor(window) {
    autobind(this, ['reflectToHistoryMiddleware']);

    this.window = window;
    this.isReflectingToStore = false;
  }

  initialize(store) {
    this.window.addEventListener('popstate', () => {
      this.reflectToStore(store);
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
      }

      return result;
    };
  }
}

export class StoreFormSynchronizer {
  constructor(form) {
    this.form = form;

    autobind(this, ['reflectToFormMiddleware']);

    const nonReactFields = form.getInputs().map(e => e.getAttribute('name'));

    this.fields = allFields.filter(f => nonReactFields.indexOf(f) >= 0);
  }

  reflectToFormMiddleware(store) {
    return next => action => {
      const result = next(action);
      const state = store.getState();

      // TODO: Remove this logging line eventually.
      console.log(state);  // eslint-disable-line

      this.fields.forEach(field => {
        const oldVal = serializers[field](
          deserializers[field](this.form.get(field))
        );
        const newVal = serializers[field](state[field]);

        if (oldVal !== newVal) {
          this.form.set(field, newVal);
        }
      });

      return result;
    };
  }

  reflectToStore(store) {
    const state = store.getState();
    const changes = {};

    this.fields.forEach(field => {
      const oldVal = serializers[field](state[field]);
      const newDeserializedVal = deserializers[field](this.form.get(field));
      const newVal = serializers[field](newDeserializedVal);

      if (oldVal !== newVal) {
        changes[field] = newDeserializedVal;
      }
    });

    if (Object.keys(changes).length) {
      store.dispatch(setState(Object.assign({}, state, changes)));
    }
  }
}
