export const EXCLUDE_ROW = 'EXCLUDE_ROW';
export const EXCLUDE_NONE = 'EXCLUDE_NONE';
export const EXCLUDE_SET = 'EXCLUDE_SET';

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

export function excludeSet(value) {
  return { type: EXCLUDE_SET, value };
}
