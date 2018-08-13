import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Schedule from './schedule';
import { scheduleLabels } from '../schedule-metadata';

export function SearchCategory({ selectedSchedule }) {
  // TODO: Set up another Redux store to track what choice has been selected
  // Will need to track which schedule has been chosen, or if vendor/contract
  // has been selected.
  return (
    <div className="html-dropdown">
      <div className="html-dropdown__trigger">
        <strong>
          Search labor categories
        </strong>
        <span>
          in {scheduleLabels[selectedSchedule]}
        </span>
      </div>
      <div className="html-dropdown__choices">
        <Schedule />
      </div>
    </div>
  );
}

export default connect(
  state => ({ selectedSchedule: state.schedule })
)(SearchCategory);
