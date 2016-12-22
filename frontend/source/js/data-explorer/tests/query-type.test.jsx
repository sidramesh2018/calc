/* global expect, describe, it, jest */
import React from 'react';

import { render, mount } from 'enzyme';
import toJson from 'enzyme-to-json';

import { QueryType } from '../components/query-type';

function setup() {
  const props = {
    queryType: 'match_exact',
    setQueryType: jest.fn(),
    idPrefix: 'zzz_',
  };

  const wrapper = render(<QueryType {...props} />);
  const mounted = mount(<QueryType {...props} />);

  return { props, wrapper, mounted };
}

describe('<QueryType>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('#zzz_match_all').val()).toBe('match_all');
    expect(wrapper.find('#zzz_match_exact').val()).toBe('match_exact');
    expect(wrapper.find('#zzz_match_phrase').val()).toBe('match_phrase');
  });

  it('matching queryType is checked', () => {
    const { wrapper } = setup();
    expect(wrapper.find('#zzz_match_all').prop('checked')).toBe(false);
    expect(wrapper.find('#zzz_match_phrase').prop('checked')).toBe(false);
    expect(wrapper.find('#zzz_match_exact').prop('checked')).toBe(true);
  });

  it('calls setQueryType fn onChange', () => {
    const { props, mounted } = setup();
    expect(props.setQueryType.mock.calls.length).toBe(0);
    mounted.find('#zzz_match_phrase')
      .simulate('change', { target: { checked: true } });
    expect(props.setQueryType.mock.calls.length).toBe(1);
    expect(props.setQueryType.mock.calls[0][0]).toBe('match_phrase');
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
