import React from 'react';
import { connect } from 'react-redux';

import { excludeNone } from './store';

function RestoreExcluded({ excluded, onClick }) {
  const len = excluded.length;
  const rows = `row${len === 1 ? '' : 's'}`;
  const handleClick = e => {
    e.preventDefault();
    onClick();
  };

  return (
    <a className="restore"
       href="?exclude="
       style={len === 0 ? { display: 'none' } : null}
       title={`${rows}: ${excluded.join(', ')}`}
       onClick={handleClick}>
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

const mapDispatchToProps = {
  onClick: excludeNone,
};

export default connect(mapStateToProps, mapDispatchToProps)(RestoreExcluded);
