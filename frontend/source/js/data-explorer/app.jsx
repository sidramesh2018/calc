import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './restore-excluded';
import { store } from './store';

export default function init({ restoreExcludedRoot }) {
  ReactDOM.render(
    <Provider store={store}>
      <RestoreExcluded />
    </Provider>,
    restoreExcludedRoot
  );
}
