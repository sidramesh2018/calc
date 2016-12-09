import React from 'react';
import classNames from 'classnames';

const getDataCellClasses = (key, sort) => ({
  cell: true,
  sorted: sort.key === key,
  [`column-${key}`]: true,
});

export const createDataCellConnector = key => Component => {
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

export class GenericDataCell extends React.Component {
  render() {
    return (
      <td className={this.props.className}>
        {this.props.value}
      </td>
    );
  }
}

GenericDataCell.propTypes = {
  className: React.PropTypes.string.isRequired,
  result: React.PropTypes.object.isRequired,
  value: React.PropTypes.any,
};
