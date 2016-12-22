/* global jest */
import React from 'react';
import { render, mount } from 'enzyme';

export default function makeSetup(Component, props) {
  return function setup(opts = null) {
    if (opts) {
      Object.assign(props, opts);
    }

    const wrapper = render(<Component {...props} />);
    const mounted = mount(<Component {...props} />);

    return { props, wrapper, mounted };
  };
}
