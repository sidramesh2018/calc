
import React from 'react';
import Loadable from 'react-loadable';

const LoadableOptionalFilters = Loadable({
  loader: () => import('./optional-filters'),
  // eslint-disable-next-line react/prop-types
  loading({ error, pastDelay }) {
    if (error) {
      return <div>Error!</div>;
    } else if (pastDelay) {
      return <div>Loading...</div>;
    }
    return null;
  },
});

export default LoadableOptionalFilters;
