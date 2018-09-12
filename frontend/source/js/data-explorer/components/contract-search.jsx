import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setSchedule as setScheduleAction } from '../actions';
import { setQueryBy as setQueryByAction } from '../actions';
import { QUERY_BY_CONTRACT} from '../constants';

export function ContractNum({ setSchedule, setQueryBy }) {
  const handleClick = (e) => {
    // unset selectedSchedule if it has been previously set
    setSchedule('');
    setQueryBy(e.target.value);
  }

  return (
    <button
      type="button"
      id={QUERY_BY_CONTRACT}
      name={QUERY_BY_CONTRACT}
      value={QUERY_BY_CONTRACT}
      onClick={handleClick}
    >
      Search by contract number
    </button>
  );
}

ContractNum.propTypes = {
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
)(ContractNum);
