/* global expect, describe, it, jest */
import toJson from 'enzyme-to-json';

import { LoadingIndicator } from '../components/loading-indicator';
import makeSetup from './testSetup';

const defaultProps = {
  error: null,
};

const setup = makeSetup(LoadingIndicator, defaultProps);

describe('<LoadingIndicator>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('.loading-indicator').exists()).toBeTruthy();
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('renders error message', () => {
    const { wrapper } = setup({ error: 'an error message' });
    expect(wrapper.find('.error-message').text()).toBe('an error message');
  });

  it('does not render an "abort" error message', () => {
    const { wrapper } = setup({ error: 'abort' });
    expect(wrapper.find('.error-message').text()).toBeFalsy();
  });
});
