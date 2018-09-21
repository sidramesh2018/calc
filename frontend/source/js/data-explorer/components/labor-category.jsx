import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import * as autocomplete from '../autocomplete';
import { setQuery } from '../actions';

import {
  QUERY_BY_SCHEDULE,
  QUERY_BY_CONTRACT,
  QUERY_BY_VENDOR,
  MAX_QUERY_LENGTH
} from '../constants';

import {
  autobind,
  handleEnter,
} from '../util';

export class LaborCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = { value: this.props.query };
    autobind(this, ['handleChange', 'handleEnter']);
  }

  componentDidMount() {
    autocomplete.initialize(this.inputEl, {
      api: this.props.api,
      getQueryType: () => this.props.queryType,
      setFieldValue: (value) => {
        this.props.setQuery(value);
      },
    });
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      this.setState({ value: nextProps.query });
    }
  }

  componentWillUnmount() {
    autocomplete.destroy(this.inputEl);
  }

  handleChange(e) {
    this.setState({ value: e.target.value });
  }

  handleEnter() {
    if (this.state.value !== this.props.query) {
      this.props.setQuery(this.state.value);
    }
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;
    let placeholder = "Type a labor category";

    if (this.props.queryBy === QUERY_BY_CONTRACT) {
      placeholder = "Type a contract number";
    } else if (this.props.queryBy === QUERY_BY_VENDOR) {
      placeholder = "Type a vendor name";
    }

    return (
      <div className="search-group">
        <label htmlFor={id} className="usa-sr-only">
          { placeholder }
        </label>
        <input
          id={id}
          name="q"
          placeholder={placeholder}
          type="text"
          className="form__inline"
          ref={(el) => { this.inputEl = el; }}
          value={this.state.value}
          onChange={this.handleChange}
          onKeyDown={handleEnter(this.handleEnter)}
          maxLength={MAX_QUERY_LENGTH}
        />
        {this.props.children}
      </div>
    );
  }
}

LaborCategory.propTypes = {
  idPrefix: PropTypes.string,
  query: PropTypes.string.isRequired,
  queryType: PropTypes.string.isRequired,
  queryBy: PropTypes.string,
  setQuery: PropTypes.func.isRequired,
  api: PropTypes.object.isRequired,
  children: PropTypes.any,
};

LaborCategory.defaultProps = {
  idPrefix: '',
  children: null,
  queryBy: QUERY_BY_SCHEDULE,
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
    queryBy: state.query_by,
  }),
  { setQuery },
)(LaborCategory);
