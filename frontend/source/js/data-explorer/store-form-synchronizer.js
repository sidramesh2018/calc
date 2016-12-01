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

export default class StoreFormSynchronizer {
  constructor(form) {
    this.form = form;
    this.reflectToFormMiddleware = this.reflectToFormMiddleware.bind(this);
  }

  setSubmitForm(submit) {
    this.submit = submit;
  }

  reflectToFormMiddleware(store) {
    return next => action => {
      const result = next(action);
      const oldVal = this.form.get('exclude');
      const newVal = serializeExcludeList(store.getState().exclude);

      if (oldVal !== newVal) {
        this.form.set('exclude', newVal);
        this.submit(true);
      }

      return result;
    };
  }

  reflectToStore(store) {
    const oldVal = serializeExcludeList(store.getState().exclude);
    const newExcludeList = deserializeExcludeList(this.form.get('exclude'));
    const newVal = serializeExcludeList(newExcludeList);

    if (oldVal !== newVal) {
      store.dispatch(excludeSet(newExcludeList));
    }
  }
}
