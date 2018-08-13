import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { setSchedule as setScheduleAction } from '../actions';
import { scheduleLabels } from '../schedule-metadata';

export function Schedule({ idPrefix, selectedSchedule, setSchedule }) {
  const handleChange = (e) => { setSchedule(e.target.value); };
  const defaultMsg = `all (${Object.keys(scheduleLabels).length}) contract vehicles`;
  // In most instances, we display legacy schedules as "Legacy Schedule," i.e., "Legacy MOBIS."
  // Here, however, we want to display the "Legacy" modifier in parenthesis after the name.
  // Since the legacy modifier only is found in schedule.full_name, we have to regex.
  const legacyPrefix = "Legacy "
  const makeInput = (value, label) => {
    const id = value.replace(/ /g, '-').toLowerCase();
    const makeLabel = (label) => {
      let scheduleLabel = label;
      let labelSuffix;
      if (label.includes(legacyPrefix)) {
        scheduleLabel = label.replace(legacyPrefix, '');
        labelSuffix = "(Legacy)";
      }
      return {scheduleLabel, labelSuffix};
    };
    const { scheduleLabel, labelSuffix } = makeLabel(label);
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
          {scheduleLabel}
          <span className="label__suffix">
            {labelSuffix}
          </span>
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
