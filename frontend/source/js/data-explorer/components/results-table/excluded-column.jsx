import React from 'react';
import { connect } from 'react-redux';

import { excludeRow } from '../../actions';
import RestoreExcluded from './restore-excluded';

export function HeaderCell() {
  return (
    <th scope="col" className="exclude">
      <RestoreExcluded />
    </th>
  );
}

function BaseDataCell({ dispatch, result }) {
  const handleExcludeRow = rowId => e => {
    e.preventDefault();
    dispatch(excludeRow(rowId));
  };

  // TODO: Tooltip / aria-label on a.exclude-row

  return (
    <td className="cell column-exclude">
      <a className="exclude-row" href="#"
         onClick={handleExcludeRow(result.id)}
         title={`Exclude ${result.labor_category} from your search`}>
        &times;
      </a>
    </td>
  );
}

BaseDataCell.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  result: React.PropTypes.object.isRequired,
};

export const DataCell = connect()(BaseDataCell);
