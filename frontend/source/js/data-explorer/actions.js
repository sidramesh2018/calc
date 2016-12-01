export const EXCLUDE_ROW = 'EXCLUDE_ROW';
export const EXCLUDE_NONE = 'EXCLUDE_NONE';
export const SET_STATE = 'SET_STATE';

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

export function setState(value) {
  return { type: SET_STATE, value };
}
