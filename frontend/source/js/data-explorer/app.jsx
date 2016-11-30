import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './restore-excluded';
import { store, excludeNone } from './store';

export default function init({ restoreExcludedRoot }) {
  function handleClick(e) {
    e.preventDefault();
    store.dispatch(excludeNone());
  }

  ReactDOM.render(
    <Provider store={store}>
      <RestoreExcluded onClick={handleClick} />
    </Provider>,
    restoreExcludedRoot
  );
}
