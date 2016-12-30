/* global expect, describe, it, jest */
import React from 'react';

import * as EducationColumn from '../components/results-table/education-column';
import makeSetup from './testSetup';

const createDataCell = (Component, props) => (
  <table><tbody><tr><Component {...props}/></tr></tbody></table>
);

describe('<EducationColumn.DataCell>', () => {
  const key = 'education_level';
  const defaultProps = {
    sort: {},
    result: { [key]: '' },
  };
  const setup = makeSetup(EducationColumn.DataCell, defaultProps, {
    createElement: createDataCell,
  });

  it('contains the value when value is non-empty', () => {
    const { mounted } = setup({ result: { [key]: 'High School' } });
    expect(mounted.text()).toBe('High School');
  });

  it('contains "N/A" when value is empty', () => {
    const { mounted } = setup();
    expect(mounted.text()).toBe('N/A');
  });
});
