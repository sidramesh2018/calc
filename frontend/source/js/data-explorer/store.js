import { createStore } from 'redux';

const EXCLUDE_ROW = 'EXCLUDE_ROW';
const EXCLUDE_NONE = 'EXCLUDE_NONE';
const EXCLUDE_SET = 'EXCLUDE_SET';

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

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

function excludeSet(value) {
  return { type: EXCLUDE_SET, value };
}

function serializeExcludeList(list) {
  return list.map(String).join(',');
}

function deserializeExcludeList(list) {
  return (list || '')
    .split(',')
    .map(x => parseInt(x, 10))
    .filter(x => !isNaN(x));
}

export const store = createStore(exclude);

export function syncStoreToForm(form, submit) {
  store.subscribe(() => {
    const oldVal = form.get('exclude');
    const newVal = serializeExcludeList(store.getState());

    if (oldVal !== newVal) {
      form.set('exclude', newVal);
      submit(true);
    }
  });

  return function updateStore() {
    const oldVal = serializeExcludeList(store.getState());
    const newExcludeList = deserializeExcludeList(form.get('exclude'));
    const newVal = serializeExcludeList(newExcludeList);

    if (oldVal !== newVal) {
      store.dispatch(excludeSet(newExcludeList));
    }
  };
}
