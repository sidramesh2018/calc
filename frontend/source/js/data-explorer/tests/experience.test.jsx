import toJson from 'enzyme-to-json';

import { MIN_EXPERIENCE, MAX_EXPERIENCE } from '../constants';
import { Experience } from '../components/experience';
import makeSetup from './testSetup';

const defaultProps = {
  min: 5,
  max: 10,
  setExperience: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(Experience, defaultProps);

// mock the global jquery object function used in <Experience>
let noUiSliderMock = jest.fn();

global.$ = () => {
  const m = jest.fn();
  m.noUiSlider = noUiSliderMock;
  m.on = jest.fn();
  return m;
};

describe('<Experience>', () => {
  // NOTE: This test does not cover any noUiSlider functionality,
  // which has all been mocked
  it('renders correctly', () => {
    const { props, wrapper } = setup();

    const minSelect = wrapper.find('select#zzz_min');
    expect(minSelect.exists()).toBeTruthy();
    expect(minSelect.prop('value')).toBe(props.min);

    const maxSelect = wrapper.find('select#zzz_max');
    expect(maxSelect.exists()).toBeTruthy();
    expect(maxSelect.prop('value')).toBe(props.max);

    const minOptions = wrapper.find('select#zzz_min > option');
    expect(minOptions.length).toBe((props.max - MIN_EXPERIENCE) + 1);

    const maxOptions = wrapper.find('select#zzz_max > option');
    expect(maxOptions.length).toBe((MAX_EXPERIENCE - props.min) + 1);

    minOptions.forEach((opt, i) => {
      expect(opt.prop('value')).toBe(i);
    });

    maxOptions.forEach((opt, i) => {
      expect(opt.prop('value')).toBe(i + props.min);
    });
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('initializes noUiSlider', () => {
    noUiSliderMock = jest.fn(); // make a new mock for ease of testing
    const { props } = setup();
    expect(noUiSliderMock.mock.calls.length).toBe(1);
    const sliderArgs = noUiSliderMock.mock.calls[0][0];
    expect(sliderArgs.start[0]).toBe(props.min);
    expect(sliderArgs.start[1]).toBe(props.max);
    expect(sliderArgs.step).toBe(1);
    expect(sliderArgs.range.min).toBe(MIN_EXPERIENCE);
    expect(sliderArgs.range.max).toBe(MAX_EXPERIENCE);
  });

  it('calls setExperience when option is selected', () => {
    const { props, mounted } = setup();
    const minSelect = mounted.find('select#zzz_min');
    minSelect.simulate('change', { target: { value: '10' } });
    expect(props.setExperience.mock.calls.length).toBe(1);
    expect(props.setExperience.mock.calls[0][0]).toBe('min');
    expect(props.setExperience.mock.calls[0][1]).toBe(10);

    const maxSelect = mounted.find('select#zzz_max');
    maxSelect.simulate('change', { target: { value: '15' } });
    expect(props.setExperience.mock.calls.length).toBe(2);
    expect(props.setExperience.mock.calls[1][0]).toBe('max');
    expect(props.setExperience.mock.calls[1][1]).toBe(15);
  });

  it('has filter_active when not set to defaults', () => {
    let { wrapper } = setup({ min: MIN_EXPERIENCE, max: MAX_EXPERIENCE });
    expect(wrapper.find('.filter_active').exists()).toBeFalsy();

    ({ wrapper } = setup({ min: 5, max: 10 }));
    expect(wrapper.find('.filter_active').exists()).toBeTruthy();
  });
});
