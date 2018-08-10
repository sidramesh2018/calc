import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { setSchedule as setScheduleAction } from '../actions';
import { scheduleLabels } from '../schedule-metadata';

export function Schedule({ idPrefix, selectedSchedule, setSchedule }) {
  const handleChange = (e) => { setSchedule(e.target.value); };
  const defaultMsg = `In all (${scheduleLabels.keys}) contract vehicles`;
  const makeInput = (value, label) => {
    const id = value.replace(/ /g, '-').toLowerCase();
    return (
      <li>
        <input
          type="radio"
          id={id}
          name={id}
          value={value}
          onChange={handleChange}
          checked={selectedSchedule === value}
        />
        <label htmlFor={id}>
          {label}
        </label>
      </li>
    );
  }

  const makeChoices = (labels) => {
    return [
      { key: '', value: '', label: defaultMsg },
    ].concat(Object.keys(labels).map(
      value => ({ value, label: labels[value] }),
    )).map(({ value, label }) => (
      makeInput(value, label)
    ));
  }

  return (
    <ul className="filter--schedule">
      {makeChoices(scheduleLabels, defaultMsg)}
    </ul>
  );
}

Schedule.propTypes = {
  selectedSchedule: PropTypes.string.isRequired,
  setSchedule: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Schedule.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ selectedSchedule: state.schedule }),
  { setSchedule: setScheduleAction },
)(Schedule);
