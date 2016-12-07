import React from 'react';
import { connect } from 'react-redux';

import * as ExcludedColumn from './excluded-column';
import * as LaborCategoryColumn from './labor-category-column';
import * as EducationColumn from './education-column';

// TODO: min_years_experience
// TODO: current_price / next_year_price / second_year_price
// TODO: idv_piid
// TODO: vendor_name
// TODO: schedule

const COLUMNS = [
  ExcludedColumn,
  LaborCategoryColumn,
  EducationColumn,
];

class ResultsTable extends React.Component {
  renderBodyRows() {
    return this.props.results.map(result => (

      <tr key={result.id}>
        {COLUMNS.map((col, i) => (
          <col.DataCell result={result} key={i} />
        ))}
      </tr>
    ));
  }

  render() {
    const id = `${this.props.idPrefix}results-table`;
    const idHref = `#${id}`;

    return (
      <table id={id} className="results has-data sortable hoverable">
        <thead>
          <tr>
            {COLUMNS.map((col, i) => (<col.HeaderCell key={i}/>))}
          </tr>
        </thead>
        <tbody>
          {this.renderBodyRows()}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={COLUMNS.length}>
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
