import React from 'react';
import classNames from 'classnames';

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

const createSortHeaderTooltip = (title, { sorted, descending }) => {
  if (!sorted) {
    return `${title}: select to sort ascending`;
  }

  if (descending) {
    return `${title}: sorted descending, select to sort ascending`;
  }

  return `${title}: sorted ascending, select to sort descending`;
};

function GenericHeaderCell({ className, tooltip, title, toggleSort }) {
  return (
    <th scope="col"
        title={tooltip}
        className={className}
        onClick={toggleSort}>
      {title}
    </th>
  );
}

GenericHeaderCell.propTypes = {
  className: React.PropTypes.string.isRequired,
  title: React.PropTypes.string.isRequired,
  tooltip: React.PropTypes.string.isRequired,
  toggleSort: React.PropTypes.func.isRequired,
};

function GenericDataCell({ className, value }) {
  return (
    <td className={className}>
      {value}
    </td>
  );
}

GenericDataCell.propTypes = {
  className: React.PropTypes.string.isRequired,
  value: React.PropTypes.any,
};

const getBaseClasses = key => ({ [`column-${key}`]: true });

const createHeaderCellConnector = (description, title, key) => component => {
  const wrappedComponent = ({ sort, setSort, children }) => {
    // TODO: Tooltip / aria-label

    const isSorted = sort.key === key;
    const classes = Object.assign({
      sortable: true,
      sorted: isSorted,
      ascending: isSorted && !sort.descending,
      descending: isSorted && sort.descending,
    }, getBaseClasses(key));

    return React.createElement(component, {
      toggleSort: createSortToggler(key, sort, setSort),
      className: classNames(classes),
      tooltip: createSortHeaderTooltip(description || title, classes),
      title,
    }, children);
  };

  wrappedComponent.propTypes = {
    sort: React.PropTypes.object.isRequired,
    setSort: React.PropTypes.func.isRequired,
    children: React.PropTypes.any,
  };

  return wrappedComponent;
};

const createDataCellConnector = key => component => {
  const wrappedComponent = ({ sort, result, children }) => {
    const classes = Object.assign({
      cell: true,
      sorted: sort.key === key,
    }, getBaseClasses(key));

    return React.createElement(component, {
      className: classNames(classes),
      value: result[key],
      result,
    }, children);
  };

  wrappedComponent.propTypes = {
    sort: React.PropTypes.object.isRequired,
    result: React.PropTypes.object.isRequired,
    children: React.PropTypes.any,
  };

  return wrappedComponent;
};

export default function createSortableColumn({
  description,
  title,
  key,
}) {
  const connectHeaderCell = createHeaderCellConnector(description, title, key);
  const connectDataCell = createDataCellConnector(key);
  const HeaderCell = connectHeaderCell(GenericHeaderCell);
  const DataCell = connectDataCell(GenericDataCell);

  return { HeaderCell, DataCell, connectDataCell };
}
