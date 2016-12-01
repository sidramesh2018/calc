export const EXCLUDE_ROW = 'EXCLUDE_ROW';
export const EXCLUDE_NONE = 'EXCLUDE_NONE';
export const SET_STATE = 'SET_STATE';
export const START_RATES_REQUEST = 'START_RATES_REQUEST';
export const COMPLETE_RATES_REQUEST = 'COMPLETE_RATES_REQUEST';

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

export function setState(value) {
  return { type: SET_STATE, value };
}

export function startRatesRequest() {
  return { type: START_RATES_REQUEST };
}

export function completeRatesRequest(error, data) {
  return {
    type: COMPLETE_RATES_REQUEST,
    error,
    data,
  };
}
