import React from 'react';
import Loadable from 'react-loadable';


export const LoadableComponent = ({ error, pastDelay }) => {
  // TODO: timeout handling?
  if (error) {
    // TODO: style this?
    return (<div>Error!</div>);
  } else if (pastDelay) {
    // TODO: spinner or something
    return (<div>Loading...</div>);
  }
  return null;
};

// `path` should be relative to the component that is being
// wrapped.
export function createLoadableComponent(path) {
  return Loadable({
    loader: () => import(path),

    // TODO: does this work?
    loading: LoadableComponent, 
  })
}
