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
} from './constants';

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
};

const fields = Object.keys(serializers);

export default class StoreFormSynchronizer {
  constructor(form) {
    this.form = form;
    this.reflectToFormMiddleware = this.reflectToFormMiddleware.bind(this);
  }

  setSubmitForm(submit) {
    this.submit = submit;
  }

  reflectToFormMiddleware(store) {
    return next => action => {
      const result = next(action);
      const state = store.getState();
      let changed = false;

      // TODO: Remove this logging line eventually.
      console.log(state);  // eslint-disable-line

      fields.forEach(field => {
        const oldVal = serializers[field](
          deserializers[field](this.form.get(field))
        );
        const newVal = serializers[field](state[field]);

        if (oldVal !== newVal) {
          this.form.set(field, newVal);
          changed = true;
        }
      });

      if (changed) {
        this.submit(true);
      }

      return result;
    };
  }

  reflectToStore(store) {
    const state = store.getState();
    const changes = {};

    fields.forEach(field => {
      const oldVal = serializers[field](state[field]);
      const newSerializedVal = deserializers[field](this.form.get(field));
      const newVal = serializers[field](newSerializedVal);

      if (oldVal !== newVal) {
        changes[field] = newSerializedVal;
      }
    });

    if (Object.keys(changes).length) {
      store.dispatch(setState(Object.assign({}, state, changes)));
    }
  }
}
