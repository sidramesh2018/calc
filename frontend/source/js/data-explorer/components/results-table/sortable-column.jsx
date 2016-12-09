import React from 'react';
import classNames from 'classnames';

import Tooltip from '../tooltip';

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
        aria-label={tooltip}
        className={className}
        onClick={toggleSort}>
      <Tooltip text={tooltip}>
        {title}
      </Tooltip>
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

const createHeaderCellConnector = (description, title, key) => Component => {
  const wrappedComponent = ({ sort, setSort }) => {
    const isSorted = sort.key === key;
    const classes = Object.assign({
      sortable: true,
      sorted: isSorted,
      ascending: isSorted && !sort.descending,
      descending: isSorted && sort.descending,
    }, getBaseClasses(key));

    return <Component
            className={classNames(classes)}
            toggleSort={createSortToggler(key, sort, setSort)}
            tooltip={createSortHeaderTooltip(description || title, classes)}
            title={title} />;
  };

  wrappedComponent.propTypes = {
    sort: React.PropTypes.object.isRequired,
    setSort: React.PropTypes.func.isRequired,
  };

  return wrappedComponent;
};

const createDataCellConnector = key => Component => {
  const wrappedComponent = ({ sort, result }) => {
    const classes = Object.assign({
      cell: true,
      sorted: sort.key === key,
    }, getBaseClasses(key));

    return <Component className={classNames(classes)}
                      value={result[key]}
                      result={result} />;
  };

  wrappedComponent.propTypes = {
    sort: React.PropTypes.object.isRequired,
    result: React.PropTypes.object.isRequired,
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
