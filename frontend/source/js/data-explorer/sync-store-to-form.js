import { excludeSet } from './actions';

function serializeExcludeList(list) {
  return list.map(String).join(',');
}

function deserializeExcludeList(list) {
  return (list || '')
    .split(',')
    .map(x => parseInt(x, 10))
    .filter(x => !isNaN(x));
}

export default function syncStoreToForm(store, form, submit) {
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
