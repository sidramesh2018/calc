import React from 'react';
import { connect } from 'react-redux';

import * as ExcludedColumn from './excluded-column';

class ResultsTable extends React.Component {
  renderHeaderRow() {
    return (
      <tr>
        <ExcludedColumn.HeaderCell />
        <th scope="col" className="sortable">Labor Category</th>
      </tr>
    );
  }

  renderBodyRows() {
    return this.props.results.map(result => {
      const lc = result.labor_category;

      // TODO: education_level
      // TODO: min_years_experience
      // TODO: current_price / next_year_price / second_year_price
      // TODO: idv_piid
      // TODO: vendor_name
      // TODO: schedule

      return (
        <tr key={result.id}>
          <ExcludedColumn.DataCell result={result} />
          <th className="cell column-labor_category" scope="row">{lc}</th>
        </tr>
      );
    });
  }

  render() {
    const id = `${this.props.idPrefix}results-table`;
    const idHref = `#${id}`;
    const numColumns = 2;

    return (
      <table id={id} className="results has-data sortable hoverable">
        <thead>
          {this.renderHeaderRow()}
        </thead>
        <tbody>
          {this.renderBodyRows()}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={numColumns}>
              <a href={idHref}>Return to the top</a>
            </td>
          </tr>
        </tfoot>
      </table>
    );
  }
}

ResultsTable.propTypes = {
  sort: React.PropTypes.object.isRequired,
  contractYear: React.PropTypes.string.isRequired,
  results: React.PropTypes.array.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string,
};

ResultsTable.defaultProps = {
  idPrefix: '',
};

function mapStateToProps(state) {
  return {
    sort: state.sort,
    contractYear: state['contract-year'],
    results: state.rates.data.results,
  };
}

export default connect(mapStateToProps)(ResultsTable);
