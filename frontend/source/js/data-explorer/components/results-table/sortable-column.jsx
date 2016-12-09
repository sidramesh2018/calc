import React from 'react';
import classNames from 'classnames';

import { handleEnterOrSpace } from '../../util';
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

class GenericHeaderCell extends React.Component {
  constructor(props) {
    super(props);
    this.state = { focused: false };
  }

  render() {
    return (
      <th scope="col"
          onFocus={() => { this.setState({ focused: true }); }}
          onBlur={() => { this.setState({ focused: false }); }}
          tabIndex="0"
          role="button"
          aria-label={this.props.tooltip}
          className={this.props.className}
          onKeyDown={handleEnterOrSpace(this.props.toggleSort)}
          onClick={this.props.toggleSort}>
        <Tooltip text={this.props.tooltip} show={this.state.focused}>
          {this.props.title}
        </Tooltip>
      </th>
    );
  }
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

const getHeaderCellClasses = (key, sort) => Object.assign({
  sortable: true,
  sorted: sort.key === key,
  ascending: sort.key === key && !sort.descending,
  descending: sort.key === key && sort.descending,
}, getBaseClasses(key));

const getDataCellClasses = (key, sort) => Object.assign({
  cell: true,
  sorted: sort.key === key,
}, getBaseClasses(key));

const createHeaderCellConnector = (description, title, key) => Component => {
  const wrappedComponent = ({ sort, setSort }) => {
    const classes = getHeaderCellClasses(key, sort);

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
  const wrappedComponent = ({ sort, result }) => (
    <Component className={classNames(getDataCellClasses(key, sort))}
               value={result[key]}
               result={result} />
  );

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
