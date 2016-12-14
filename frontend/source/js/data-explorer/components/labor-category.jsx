import React from 'react';
import { connect } from 'react-redux';

import * as autocomplete from '../autocomplete';
import { setQuery } from '../actions';

import {
  autobind,
  handleEnter,
} from '../util';

class LaborCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = { value: this.props.query };
    autobind(this, ['handleChange', 'handleEnter']);
  }

  handleChange(e) {
    this.setState({ value: e.target.value });
  }

  handleEnter() {
    this.props.setQuery(this.state.value);
  }

  componentDidMount() {
    autocomplete.initialize(this.inputEl, {
      api: this.props.api,
      getQueryType: () => this.props.queryType,
      getFieldValue: () => this.state.value,
      setFieldValue: value => { this.setState({ value }); },
    });
  }

  componentWillUnmount() {
    autocomplete.destroy(this.inputEl);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      this.setState({ value: nextProps.query });
    }
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;

    return (
      <div>
        <input id={id} name="q" placeholder="Type a labor category"
               className="search u-full-width" type="text"
               ref={el => { this.inputEl = el; }}
               value={this.state.value}
               onChange={this.handleChange}
               onKeyDown={handleEnter(this.handleEnter)} />
        <label htmlFor={id} className="sr-only">Type a labor category</label>
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
};

LaborCategory.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
  }),
  { setQuery }
)(LaborCategory);
