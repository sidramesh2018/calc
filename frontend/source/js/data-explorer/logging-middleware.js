/* global window */

export default function loggingMiddleware(store) {
  return next => action => {
    if (!(window.console && window.console.groupCollapsed)) {
      return next(action);
    }

    /* eslint-disable */
    console.groupCollapsed(action.type);
    console.log('Begin state', store.getState());

    const result = next(action);

    console.log('End state', store.getState());
    console.groupEnd();
    /* eslint-enable */

    return result;
  };
}
