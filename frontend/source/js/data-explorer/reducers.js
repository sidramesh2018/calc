import { combineReducers } from 'redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  DEFAULT_CONTRACT_YEAR,
} from './constants';

import {
  EXCLUDE_NONE,
  EXCLUDE_ROW,
  SET_STATE,
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

const combinedReducer = combineReducers({
  exclude,
  q,
  education,
  min_experience: minExperience,
  max_experience: maxExperience,
  'contract-year': contractYear,
});

export default (state, action) => {
  if (action.type === SET_STATE) {
    return action.value;
  }
  return combinedReducer(state, action);
};
