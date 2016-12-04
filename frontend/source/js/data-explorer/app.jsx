import ReactDOM from 'react-dom';
import React from 'react';
import { Provider } from 'react-redux';

import RestoreExcluded from './components/restore-excluded';
import Description from './components/description';
import Highlights from './components/highlights';
import Histogram from './components/histogram';
import ProposedPrice from './components/proposed-price';
import EducationLevel from './components/education-level';

export default function init({
  store,
  restoreExcludedRoot,
  descriptionRoot,
  highlightsRoot,
  histogramRoot,
  proposedPriceRoot,
  educationLevelRoot,
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

  ReactDOM.render(
    <Provider store={store}>
      <Histogram />
    </Provider>,
    histogramRoot
  );

  ReactDOM.render(
    <Provider store={store}>
      <ProposedPrice />
    </Provider>,
    proposedPriceRoot
  );

  ReactDOM.render(
    <Provider store={store}>
      <EducationLevel />
    </Provider>,
    educationLevelRoot
  );
}
