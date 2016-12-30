/* global expect, describe, it, jest */
import React from 'react';

import * as EducationColumn from '../components/results-table/education-column';
import makeSetup from './testSetup';

// We need this to avoid a validateDOMNesting warning.
const createDataCell = (Component, props) => (
  <table><tbody><tr><Component {...props}/></tr></tbody></table>
);

const makeDataCellSetup = (column, defaultProps) => makeSetup(
  column.DataCell.WrappedComponent, defaultProps, {
    createElement: createDataCell,
  }
);

describe('<EducationColumn.DataCell>', () => {
  const setup = makeDataCellSetup(EducationColumn, { value: '' });

  it('contains the value when value is non-empty', () => {
    const { mounted } = setup({ value: 'High School' });
    expect(mounted.text()).toBe('High School');
  });

  it('contains "N/A" when value is empty', () => {
    const { mounted } = setup();
    expect(mounted.text()).toBe('N/A');
  });
});
