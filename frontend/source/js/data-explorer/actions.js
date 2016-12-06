export const EXCLUDE_ROW = 'EXCLUDE_ROW';
export const EXCLUDE_NONE = 'EXCLUDE_NONE';
export const SET_STATE = 'SET_STATE';
export const RESET_STATE = 'RESET_STATE';
export const START_RATES_REQUEST = 'START_RATES_REQUEST';
export const COMPLETE_RATES_REQUEST = 'COMPLETE_RATES_REQUEST';
export const INVALIDATE_RATES = 'INVALIDATE_RATES';
export const SET_SORT = 'SET_SORT';
export const SET_PROPOSED_PRICE = 'SET_PROPOSED_PRICE';
export const SET_EXPERIENCE = 'SET_EXPERIENCE';
export const TOGGLE_EDU_LEVEL = 'TOGGLE_EDU_LEVEL';

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

export function setState(value) {
  return { type: SET_STATE, value };
}

export function resetState() {
  return { type: RESET_STATE };
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

export function invalidateRates() {
  return { type: INVALIDATE_RATES };
}

export function setSort({ key, descending }) {
  return {
    type: SET_SORT,
    key,
    descending,
  };
}

export function setProposedPrice(price) {
  return { type: SET_PROPOSED_PRICE, price };
}

export function setExperience(subtype, years) {
  return { type: SET_EXPERIENCE, subtype, years };
}

export function toggleEducationLevel(level) {
  return { type: TOGGLE_EDU_LEVEL, level };
}
