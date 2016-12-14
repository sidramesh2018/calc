/* global window */

/**
 * This file contains temporary Redux middleware useful for
 * migrating from legacy CALC 1.0's Data Explorer to the new
 * React/Redux implementation.
 */

export function StoreStateFieldWatcher() {
  const watchers = [];

  return {
    watch(name, cb) {
      watchers.push([name, cb]);
    },

    middleware(store) {
      return next => action => {
        const oldState = store.getState();
        const result = next(action);
        const newState = store.getState();

        watchers.forEach(([name, cb]) => {
          if (oldState[name] !== newState[name]) {
            cb();
          }
        });

        return result;
      };
    },
  };
}

export function loggingMiddleware(store) {
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
