import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './restore-excluded';
import Description from './description';

export default function init({
  store,
  restoreExcludedRoot,
  descriptionRoot,
}) {
  ReactDOM.render(
    <Provider store={store}>
      <RestoreExcluded />
    </Provider>,
    restoreExcludedRoot
  );

  ReactDOM.render(
    <Provider store={store}>
      <Description />
    </Provider>,
    descriptionRoot
  );
}
