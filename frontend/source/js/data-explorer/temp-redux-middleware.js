/**
 * This file contains temporary Redux middleware useful for
 * migrating from legacy CALC 1.0's Data Explorer to the new
 * React/Redux implementation.
 */

import {
  setState,
} from './actions';

import {
  autobind,
} from './util';

import {
  allFields,
  serializers,
  deserializers,
} from './serialization';

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

export class StoreFormSynchronizer {
  constructor(form) {
    this.form = form;

    autobind(this, ['reflectToFormMiddleware']);

    const nonReactFields = form.getInputs().map(e => e.getAttribute('name'));

    this.fields = allFields.filter(f => nonReactFields.indexOf(f) >= 0);
  }

  reflectToFormMiddleware(store) {
    return next => action => {
      const result = next(action);
      const state = store.getState();

      this.fields.forEach(field => {
        const oldVal = serializers[field](
          deserializers[field](this.form.get(field))
        );
        const newVal = serializers[field](state[field]);

        if (oldVal !== newVal) {
          this.form.set(field, newVal);
        }
      });

      return result;
    };
  }

  reflectToStore(store) {
    const state = store.getState();
    const changes = {};

    this.fields.forEach(field => {
      const oldVal = serializers[field](state[field]);
      const newDeserializedVal = deserializers[field](this.form.get(field));
      const newVal = serializers[field](newDeserializedVal);

      if (oldVal !== newVal) {
        changes[field] = newDeserializedVal;
      }
    });

    if (Object.keys(changes).length) {
      store.dispatch(setState(Object.assign({}, state, changes)));
    }
  }
}
