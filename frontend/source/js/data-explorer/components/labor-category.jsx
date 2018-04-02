import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { Creatable } from 'react-select';

import { setQuery } from '../actions';

import {
  autobind,
  queryStringToValuesArray,
  valuesArrayToQueryString,
} from '../util';

// TODO: MAX_QUERY_LENGTH anywhere?
// TODO: initial query is cleared once new items are added
// TODO: highlight suggestion items in dropdown
// TODO: remove loading-indicator
// TODO: fix api/views.py to use csv-style parsing
// TODO: take out arrow

export class LaborCategory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      value: queryStringToValuesArray(this.props.query),
      isLoading: false,
      options: [],
    };
    autobind(this, [
      'handleChange', 'loadOptions', 'handleInputChange',
      'clearOptionsAndStopLoading',
    ]);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      this.setState({ value: queryStringToValuesArray(nextProps.query) });
    }
  }

  clearOptionsAndStopLoading() {
    this.setState({ options: [], isLoading: false });
    if (this._autoCompReq) { this._autoCompReq.abort(); }
  }

  handleChange(values) {
    this.setState({ value: values, options: [] });
    this.props.setQuery(valuesArrayToQueryString(values));
  }

  handleInputChange(val) {
    if (val.length >= 3) {
      this.loadOptions(val);
    } else {
      this.clearOptionsAndStopLoading();
    }
  }

  loadOptions(input) {
    if (!input) {
      this.setState({ options: [], isLoading: false });
      return;
    }

    if (this._autoCompReq) { this._autoCompReq.abort(); }

    this.setState({ isLoading: true });
    this._autoCompReq = this.props.api.get({
      uri: 'search/',
      data: {
        q: input,
        query_type: this.props.queryType,
      },
    }, (error, result) => {
      this._autoCompReq = null;
      if (error) {
        this.setState({ options: [], isLoading: false });
        return;
      }

      const categories = result.slice(0, 20).map(d => ({
        name: d.labor_category,
        count: d.count,
      }));
      this.setState({ options: categories, isLoading: false });
    });
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;
    const className = 'form__inline';

    return (
      <div>
        <Creatable
          id={id}
          name="q"
          placeholder="Type a labor category"
          className={className}
          multi
          value={this.state.value}
          onChange={this.handleChange}
          onInputChange={this.handleInputChange}
          valueKey="name"
          labelKey="name"
          promptTextCreator={label => `Search for "${label}"`}
          noResultsText="No matches found"
          options={this.state.options}
          isLoading={this.state.isLoading}
        />

        <label htmlFor={id} className="sr-only">Type a labor category</label>
        {this.props.children}
      </div>
    );
  }
}

LaborCategory.propTypes = {
  idPrefix: PropTypes.string,
  query: PropTypes.string.isRequired,
  queryType: PropTypes.string.isRequired,
  setQuery: PropTypes.func.isRequired,
  api: PropTypes.object.isRequired,
  children: PropTypes.any,
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
