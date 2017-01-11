import toJson from 'enzyme-to-json';

import { EducationLevel } from '../components/education-level';
import makeSetup from './testSetup';
import { EDU_LABELS } from '../constants';

const defaultProps = {
  levels: ['MA', 'PHD'],
  idPrefix: 'zzz_',
  toggleEducationLevel: jest.fn(),
};

const setup = makeSetup(EducationLevel, defaultProps);

describe('<EducationLevel>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();

    Object.keys(EDU_LABELS).forEach((key) => {
      const checkbox = wrapper.find(`input[value="${key}"][type="checkbox"]`);
      expect(checkbox.exists()).toBeTruthy();
      const id = `zzz_${key}`;
      expect(checkbox.prop('id')).toBe(id);

      if (defaultProps.levels.indexOf(key) >= 0) {
        expect(checkbox.prop('checked')).toBeTruthy();
      } else {
        expect(checkbox.prop('checked')).toBeFalsy();
      }

      const label = wrapper.find(`label[htmlFor="${id}"]`);
      expect(label.exists()).toBeTruthy();
      expect(label.text()).toBe(EDU_LABELS[key]);
    });
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('has filter_active class when levels are selected', () => {
    let { wrapper } = setup({ levels: [] });
    expect(wrapper.find('a.filter_active').exists()).toBeFalsy();

    ({ wrapper } = setup({ levels: ['HS'] }));
    expect(wrapper.find('a.filter_active').exists()).toBeTruthy();
  });

  it('calls toggleEducationLevel when checkbox is clicked', () => {
    const { props, mounted } = setup();
    expect(props.toggleEducationLevel.mock.calls.length).toBe(0);

    mounted.find('input[value="HS"]')
      .simulate('change', { target: { checked: true } });

    expect(props.toggleEducationLevel.mock.calls.length).toBe(1);
    expect(props.toggleEducationLevel.mock.calls[0][0]).toBe('HS');
  });
});
