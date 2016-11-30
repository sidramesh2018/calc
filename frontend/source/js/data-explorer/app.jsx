import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './restore-excluded';

export default function init({ store, restoreExcludedRoot }) {
  ReactDOM.render(
    <Provider store={store}>
      <RestoreExcluded />
    </Provider>,
    restoreExcludedRoot
  );
}
