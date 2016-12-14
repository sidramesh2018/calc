import React from 'react';
import { connect } from 'react-redux';

import { makeOptions } from './util';
import { setBusinessSize as setBusinessSizeAction } from '../actions';
import { BUSINESS_SIZE_LABELS } from '../constants';

function BusinessSize({ idPrefix, size, setSize }) {
  const id = `${idPrefix}business_size`;
  const handleChange = e => { setSize(e.target.value); };

  return (
    <div className="filter filter-business_size">
      <label htmlFor={id}>Business size:</label>
      <select id={id} name="business_size"
              value={size} onChange={handleChange}>
        {makeOptions(BUSINESS_SIZE_LABELS)}
      </select>
    </div>
  );
}

BusinessSize.propTypes = {
  size: React.PropTypes.string.isRequired,
  setSize: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string,
};

BusinessSize.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ size: state.business_size }),
  { setSize: setBusinessSizeAction }
)(BusinessSize);
