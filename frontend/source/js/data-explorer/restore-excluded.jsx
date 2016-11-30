import React from 'react';
import { connect } from 'react-redux';

function RestoreExcluded({ excluded, onClick }) {
  const len = excluded.length;
  const rows = `row${len === 1 ? '' : 's'}`;

  return (
    <a className="restore"
       href="?exclude="
       style={len === 0 ? { display: 'none' } : null}
       title={`${rows}: ${excluded.join(', ')}`}
       onClick={onClick}>
         {len > 0 ? `★ Restore ${len} ${rows}` : ''}
    </a>
  );
}

RestoreExcluded.propTypes = {
  excluded: React.PropTypes.array.isRequired,
  onClick: React.PropTypes.func.isRequired,
};

function mapStateToProps(state) {
  return {
    excluded: state,
  };
}

export default connect(mapStateToProps)(RestoreExcluded);
