import React from 'react';
import { connect } from 'react-redux';
import { AsyncCreatable } from 'react-select';

import { setQuery } from '../actions';

import {
  autobind,
  filterActive,
} from '../util';

// TODO: MAX_QUERY_LENGTH anywhere?
// TODO: Close/clear suggestions dropdown after select item
// TODO: initial query is cleared once new items are added

let autoCompReq = null; // TODO: better place to put this?

function queryToValues(query) {
  if (!query || query.trim().length === 0) {
    return null;
  }

  return query.split(',')
    .map(q => ({ name: q.trim() }))
    .filter(q => q.name.length !== 0); // TODO: maybe deserialization should do this
}

export class LaborCategory extends React.Component {
  constructor(props) {
    super(props);

    this.state = { value: queryToValues(this.props.query) };
    autobind(this, ['handleChange', 'loadOptions']);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      this.setState({ value: queryToValues(nextProps.query) });
    }
  }

  handleChange(value) {
    this.setState({ value });

    const query = value.map(v => v.name).join(', ');
    this.props.setQuery(query);
  }

  loadOptions(input, callback) {
    if (!input) {
      callback(null, { options: [] });
      return;
    }

    if (autoCompReq) { autoCompReq.abort(); }
    autoCompReq = this.props.api.get({
      uri: 'search/',
      data: {
        q: input,
        query_type: this.props.queryType,
      },
    }, (error, result) => {
      autoCompReq = null;
      if (error) {
        return callback(null, { options: [] });
      }

      const categories = result.slice(0, 20).map(d => ({
        name: d.labor_category,
        count: d.count,
      }));
      return callback(null, { options: categories });
    });
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;
    const className = filterActive(this.props.query !== '', 'form__inline');

    return (
      <div>
        <AsyncCreatable
          id={id}
          name="q"
          placeholder="Type a labor category"
          className={className}
          multi
          value={this.state.value}
          onChange={this.handleChange}
          valueKey="name"
          labelKey="name"
          loadOptions={this.loadOptions}
        />

        <label htmlFor={id} className="sr-only">Type a labor category</label>
        {this.props.children}
      </div>
    );
  }
}

LaborCategory.propTypes = {
  idPrefix: React.PropTypes.string,
  query: React.PropTypes.string.isRequired,
  queryType: React.PropTypes.string.isRequired,
  setQuery: React.PropTypes.func.isRequired,
  api: React.PropTypes.object.isRequired,
  children: React.PropTypes.any,
};

LaborCategory.defaultProps = {
  idPrefix: '',
  children: null,
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
  }),
  { setQuery },
)(LaborCategory);
