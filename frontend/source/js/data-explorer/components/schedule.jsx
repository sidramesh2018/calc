import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setSchedule as setScheduleAction } from '../actions';
import { scheduleLabels } from '../schedule-metadata';

export function Schedule({ selectedSchedule, setSchedule }) {
  const handleChange = (e) => { setSchedule(e.target.value); };
  const defaultMsg = `In all ${Object.keys(scheduleLabels).length} of these contract vehicles:`;
  // In most instances, we display legacy schedules as "Legacy Schedule," i.e., "Legacy MOBIS."
  // Here, however, we want to display the "Legacy" modifier in parenthesis after the name.
  // Since the legacy modifier only is found in schedule.full_name, we have to regex.
  const legacyPrefix = "Legacy ";
  const makeInput = (value, label) => {
    const id = value.replace(/ /g, '-').toLowerCase() || 'all-schedules';
    const makeLabel = (title) => {
      let scheduleLabel = title;
      let labelSuffix;
      if (title.includes(legacyPrefix)) {
        scheduleLabel = title.replace(legacyPrefix, '');
        labelSuffix = "(Legacy)";
      }
      return { scheduleLabel, labelSuffix };
    };
    const { scheduleLabel, labelSuffix } = makeLabel(label);
    return (
      <li key={id}>
        <input
          type="radio"
          id={id}
          name={id}
          value={value}
          onChange={handleChange}
          checked={selectedSchedule === value}
        />
        <label htmlFor={id}>
          {scheduleLabel}
          <span className="label__suffix">
            {labelSuffix}
          </span>
        </label>
      </li>
    );
  };

  const makeChoices = labels => [
    { key: '', value: '', label: defaultMsg },
  ].concat(Object.keys(labels).map(
    value => ({ value, label: labels[value] }),
  )).map(({ value, label }) => (
    makeInput(value, label)
  ));

  return (
    <ul className="filter--schedule">
      {makeChoices(scheduleLabels, defaultMsg)}
    </ul>
  );
}

Schedule.propTypes = {
  selectedSchedule: PropTypes.string,
  setSchedule: PropTypes.func.isRequired,
};

export default connect(
  state => ({ selectedSchedule: state.schedule }),
  { setSchedule: setScheduleAction },
)(Schedule);
