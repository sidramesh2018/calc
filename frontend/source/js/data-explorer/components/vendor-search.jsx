import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setSchedule as setScheduleAction } from '../actions';
import { setQueryBy as setQueryByAction } from '../actions';
import { QUERY_BY_VENDOR} from '../constants';

export function Vendor({ setSchedule, setQueryBy }) {
  const handleClick = (e) => {
    // unset selectedSchedule if it has been previously set
    setSchedule('');
    setQueryBy(e.target.value);
  }

  return (
    <button
      type="button"
      id={QUERY_BY_VENDOR}
      name={QUERY_BY_VENDOR}
      value={QUERY_BY_VENDOR}
      onClick={handleClick}
    >
      Search by vendor name
    </button>
  );
}

Vendor.propTypes = {
  setQueryBy: PropTypes.func.isRequired,
};

export default connect(
  state => ({
    selectedSchedule: state.schedule,
    queryBy: state.query_by,
  }),
  {
    setSchedule: setScheduleAction,
    setQueryBy: setQueryByAction,
  },
)(Vendor);
