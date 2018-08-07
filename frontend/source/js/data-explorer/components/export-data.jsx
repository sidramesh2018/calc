import PropTypes from 'prop-types';
import * as qs from 'querystring';

import React from 'react';
import { connect } from 'react-redux';

import { getRatesParameters } from '../rates-request';
import { API_BASE, API_PATH_RATES_CSV } from '../api';

export function ExportData({ querystring }) {
  const href = `${API_BASE}${API_PATH_RATES_CSV}/${querystring}`;

  return (
    <button
      className="button-gray-icon csv export-data"
      title="Click to export your search results to an Excel file (CSV)"
      href={href}
    >
      Export data <span>.csv</span>
    </button>
  );
}

ExportData.propTypes = {
  querystring: PropTypes.string.isRequired,
};

function mapStateToProps(state) {
  return {
    querystring: `?${qs.stringify(getRatesParameters(state))}`,
  };
}

export default connect(mapStateToProps)(ExportData);
