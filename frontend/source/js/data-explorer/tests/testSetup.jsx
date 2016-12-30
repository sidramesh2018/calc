/* global jest */
import React from 'react';
import { shallow, mount } from 'enzyme';

export default function makeSetup(Component, defaultProps) {
  return function setup(extraProps = {}) {
    const props = Object.assign({}, defaultProps, extraProps);
    const wrapper = shallow(<Component {...props} />);
    const mounted = mount(<Component {...props} />);

    return { props, wrapper, mounted };
  };
}
