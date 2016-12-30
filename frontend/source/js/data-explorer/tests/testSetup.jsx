/* global jest */
import React from 'react';
import { shallow, mount } from 'enzyme';

export default function makeSetup(Component, defaultProps = {}, options = {}) {
  const createElement = options.createElement || React.createElement;

  return function setup(extraProps = {}) {
    const props = Object.assign({}, defaultProps, extraProps);
    const el = createElement(Component, props);
    const wrapper = shallow(el);
    const mounted = mount(el);

    return { props, wrapper, mounted };
  };
}
