import React from 'react';
import { connect } from 'react-redux';

function LoadingIndicator({ error }) {
  return (
    <div className="loading-indicator">
      <p className="message">Loading results...</p>
      <div className="error-message">
        { error === 'abort' ? '' : error }
      </div>
    </div>
  );
}

LoadingIndicator.propTypes = {
  error: React.PropTypes.string,
};

export default connect(
  state => ({ error: state.rates.error })
)(LoadingIndicator);
