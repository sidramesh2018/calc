import { combineReducers } from 'redux';

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

function contractYear(state = 'current') {
  // TODO: Create actions to change this.
  return state;
}

function q(state = '') {
  // TODO: Create actions to change this.
  return state;
}

const combinedReducer = combineReducers({
  exclude,
  q,
  'contract-year': contractYear,
});

export default (state, action) => {
  if (action.type === SET_STATE) {
    return action.value;
  }
  return combinedReducer(state, action);
};
