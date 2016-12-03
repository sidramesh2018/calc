import { combineReducers } from 'redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  DEFAULT_CONTRACT_YEAR,
  EMPTY_RATES_DATA,
  DEFAULT_SORT,
  DEFAULT_QUERY_TYPE,
} from './constants';

import {
  EXCLUDE_NONE,
  EXCLUDE_ROW,
  SET_STATE,
  COMPLETE_RATES_REQUEST,
  START_RATES_REQUEST,
  SET_SORT,
  SET_PROPOSED_PRICE,
} from './actions';

function exclude(state = [], action) {
  switch (action.type) {
    case EXCLUDE_NONE:
      return [];
    case EXCLUDE_ROW:
      return state.concat(action.rowId);
    default:
      return state;
  }
}

function contractYear(state = DEFAULT_CONTRACT_YEAR) {
  // TODO: Create actions to change this.
  return state;
}

function q(state = '') {
  // TODO: Create actions to change this.
  return state;
}

function education(state = []) {
  // TODO: Create actions to change this.
  return state;
}

function minExperience(state = MIN_EXPERIENCE) {
  // TODO: Create actions to change this.
  return state;
}

function maxExperience(state = MAX_EXPERIENCE) {
  // TODO: Create actions to change this.
  return state;
}

function site(state = '') {
  // TODO: Create actions to change this.
  return state;
}

function businessSize(state = '') {
  // TODO: Create actions to change this.
  return state;
}

function schedule(state = '') {
  // TODO: Create actions to change this.
  return state;
}

function proposedPrice(state = 0, action) {
  if (action.type === SET_PROPOSED_PRICE) {
    return action.price;
  }
  return state;
}

function rates(state = {
  error: null,
  data: EMPTY_RATES_DATA,
  inProgress: true,
  stale: true,
}, action) {
  const normalizeData = d => {
    if (d && d.results && d.results.length) {
      return d;
    }
    return EMPTY_RATES_DATA;
  };

  switch (action.type) {
    case START_RATES_REQUEST:
      return Object.assign({}, state, {
        inProgress: true,
        error: null,
        stale: false,
      });
    case COMPLETE_RATES_REQUEST:
      return {
        inProgress: false,
        error: action.error,
        data: normalizeData(action.data),
        stale: false,
      };
    default:
      return state;
  }
}

function sort(state = DEFAULT_SORT, action) {
  if (action.type === SET_SORT) {
    return { key: action.key, descending: action.descending };
  }
  return state;
}

function queryType(state = DEFAULT_QUERY_TYPE) {
  // TODO: Create actions to change this.
  return state;
}

const combinedReducer = combineReducers({
  exclude,
  q,
  education,
  min_experience: minExperience,
  max_experience: maxExperience,
  'contract-year': contractYear,
  site,
  business_size: businessSize,
  schedule,
  rates,
  'proposed-price': proposedPrice,
  sort,
  query_type: queryType,
});

export default (state, action) => {
  if (action.type === SET_STATE) {
    return action.value;
  }
  return combinedReducer(state, action);
};
