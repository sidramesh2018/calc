import React from 'react';
import { connect } from 'react-redux';
import classNames from 'classnames';

import { setSort } from '../../actions';

const KEY = 'labor_category';

function BaseHeaderCell({ sort, dispatch }) {
  // TODO: Tooltip / aria-label

  const handleClick = () => {
    let descending = false;

    if (sort.key === KEY && !sort.descending) {
      descending = true;
    }

    dispatch(setSort({
      key: KEY,
      descending,
    }));
  };

  const classes = {
    sortable: true,
    sorted: sort.key === KEY,
    ascending: sort.key === KEY && !sort.descending,
    descending: sort.key === KEY && sort.descending,
  };

  classes[`column-${KEY}`] = true;

  return (
    <th scope="col"
        className={classNames(classes)}
        onClick={handleClick}>
      Labor Category
    </th>
  );
}

BaseHeaderCell.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  sort: React.PropTypes.object.isRequired,
};

export const HeaderCell = connect(
  state => ({ sort: state.sort })
)(BaseHeaderCell);

function BaseDataCell({ sort, result }) {
  const classes = {
    cell: true,
    sorted: sort.key === KEY,
  };

  classes[`column-${KEY}`] = true;

  return (
    <th className={classNames(classes)} scope="row">
      {result.labor_category}
    </th>
  );
}

BaseDataCell.propTypes = {
  sort: React.PropTypes.object.isRequired,
  result: React.PropTypes.object.isRequired,
};

export const DataCell = connect(
  state => ({ sort: state.sort })
)(BaseDataCell);
