import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { makeOptions } from './util';
import { setSchedule as setScheduleAction } from '../actions';
import { scheduleLabels } from '../schedule-metadata';

export function Schedule({ idPrefix, schedule, setSchedule }) {
  const id = `${idPrefix}schedule`;
  const handleChange = (e) => { setSchedule(e.target.value); };
  const defaultMsg = 'Any contracting vehicle';

  return (
    <div className="filter--schedule">
      <label htmlFor={id} className="usa-sr-only">Select a contract vehicle:</label>
      <select
        id={id} name="schedule" value={schedule}
        onChange={handleChange}
        className={filterActive(schedule !== '')}
      >
        {makeOptions(scheduleLabels, defaultMsg)}
      </select>
    </div>
  );
}

Schedule.propTypes = {
  schedule: PropTypes.string.isRequired,
  setSchedule: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Schedule.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ schedule: state.schedule }),
  { setSchedule: setScheduleAction },
)(Schedule);
