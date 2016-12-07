import React from 'react';
import { connect } from 'react-redux';

import { setSort as setSortAction } from '../../actions';

const createSortToggler = (key, sort, setSort) => () => {
  let descending = false;

  if (sort.key === key && !sort.descending) {
    descending = true;
  }

  setSort({
    key,
    descending,
  });
};

export default function createSortableColumn(key) {
  const connectToStore = connect(
    state => ({ sort: state.sort }),
    { setSort: setSortAction }
  );

  const baseClasses = {
    [`column-${key}`]: true,
  };

  const connectHeaderCell = component => {
    const wrappedComponent = ({ sort, setSort, children }) => {
      // TODO: Tooltip / aria-label

      const isSorted = sort.key === key;
      const classes = Object.assign({
        sortable: true,
        sorted: isSorted,
        ascending: isSorted && !sort.descending,
        descending: isSorted && sort.descending,
      }, baseClasses);

      return React.createElement(component, {
        toggleSort: createSortToggler(key, sort, setSort),
        baseClasses: classes,
      }, children);
    };

    wrappedComponent.propTypes = {
      sort: React.PropTypes.object.isRequired,
      setSort: React.PropTypes.func.isRequired,
      children: React.PropTypes.any,
    };

    return connectToStore(wrappedComponent);
  };

  const connectDataCell = component => {
    const wrappedComponent = ({ sort, result, children }) => {
      const classes = Object.assign({
        cell: true,
        sorted: sort.key === key,
      }, baseClasses);

      return React.createElement(component, {
        baseClasses: classes,
        result,
      }, children);
    };

    wrappedComponent.propTypes = {
      sort: React.PropTypes.object.isRequired,
      result: React.PropTypes.object.isRequired,
      children: React.PropTypes.any,
    };

    return connectToStore(wrappedComponent);
  };

  return { connectHeaderCell, connectDataCell };
}
