/* global expect, describe, it */
import React from 'react';
import { render } from 'enzyme';

import { Highlights } from '../components/highlights.jsx';

function setup() {
  const props = {
    stdDeviation: 1.1,
    avgPrice: 2.1,
    proposedPrice: 5,
  };

  const enzymeWrapper = render(<Highlights {...props} />);

  return {
    props,
    enzymeWrapper,
  };
}

describe('<Highlights>', () => {
  it('should render self', () => {
    const { enzymeWrapper } = setup();

    expect(enzymeWrapper.find('.sd-highlight').first().text()).toBe('$1');
  });
});
