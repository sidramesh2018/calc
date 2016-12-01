import { combineReducers } from 'redux';

import {
  EXCLUDE_NONE,
  EXCLUDE_ROW,
  EXCLUDE_SET,
} from './actions';

function exclude(state = [], action) {
  switch (action.type) {
    case EXCLUDE_NONE:
      return [];
    case EXCLUDE_ROW:
      return state.concat(action.rowId);
    case EXCLUDE_SET:
      return action.value;
    default:
      return state;
  }
}

export default combineReducers({
  exclude,
});
