import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './restore-excluded';
import Description from './description';
import Highlights from './highlights';

export default function init({
  store,
  restoreExcludedRoot,
  descriptionRoot,
  highlightsRoot,
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

  ReactDOM.render(
    <Provider store={store}>
      <Highlights />
    </Provider>,
    highlightsRoot
  );
}
