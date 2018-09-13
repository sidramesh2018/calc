import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setQueryBy as setQueryByAction } from '../actions';
import Schedule from './schedule';
import Vendor from './vendor-search';
import ContractNum from './contract-search';
import {
  QUERY_BY_SCHEDULE,
  QUERY_BY_VENDOR,
  QUERY_BY_CONTRACT,
  DEFAULT_QUERY_BY
} from '../constants';
import { scheduleLabels } from '../schedule-metadata';

import {
  autobind,
  handleEnterOrSpace,
} from '../util';


export class SearchCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
    };
    autobind(this, ['toggleDropdown', 'closeMenuOnClick', 'createButtonText', ]);
  }

  toggleDropdown() {
    this.setState({
      expanded: !this.state.expanded, /* eslint-disable-line react/no-access-state-in-setstate */
    });
  }

  closeMenuOnClick() {
    this.setState({
      expanded: false,
    });
  }

  createButtonText() {
    const {
      selectedSchedule,
      queryBy,
      queryBySchedule,
      queryByVendor,
      queryByContract
    } = this.props;
    let searchSummary;
    if (queryBy === queryBySchedule) {
      let extraContext;
      let allSchedsLabel = `${Object.keys(scheduleLabels).length} contract vehicles`;

      if (!this.state.expanded) {
        extraContext =(
          <span>
            in
            {' '}
            { scheduleLabels[selectedSchedule] || allSchedsLabel }
          </span>
        );
      };

      searchSummary = (
        <div>
          <strong>
            Search labor categories
          </strong>
          { extraContext }
        </div>
      );
    } else if (queryBy == queryByVendor) {
      searchSummary = (
        <strong>Search by vendor name</strong>
      );
    } else if (queryBy == queryByContract) {
      searchSummary = (
        <strong>Search by contract number</strong>
      );
    }
    return searchSummary;
  }

  render() {
    return (
      <div className="html-dropdown">
        <button
          type="button"
          className="html-dropdown__trigger"
          aria-controls="data-explorer__search-category" /* eslint-disable-line jsx-a11y/aria-proptypes */
          onClick={this.toggleDropdown}
          onKeyDown={handleEnterOrSpace(this.toggleDropdown)}
          aria-expanded={this.state.expanded}
        >
          { this.createButtonText() }
        </button>
        {/* setting a key event on this div makes it impossible to select
          * an option with the keyboard.
          * TODO: fix this after contract/vendor name are added and the HTML is in final form. */}
        <div /* eslint-disable-line max-len, jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus */
          className="html-dropdown__choices"
          id="data-explorer__search-category"
          onClick={this.closeMenuOnClick}
          aria-hidden={!this.state.expanded}
          role="menu"
        >
          {/* TODO: "all schedules" no longer works as a selector when contract or vendor are selected? */}
          <Schedule />
          <h3>Search vendors and contracts</h3>
          {/* TODO: Add checkmarks to these as background images on buttons when selected */}
          <Vendor />
          <ContractNum />
        </div>
      </div>
    );
  }
}

SearchCategory.propTypes = {
  selectedSchedule: PropTypes.string,
  queryBySchedule: PropTypes.string.isRequired,
  queryByVendor: PropTypes.string.isRequired,
  queryByContract: PropTypes.string.isRequired,
};

SearchCategory.defaultProps = {
  selectedSchedule: '',
  queryBySchedule: QUERY_BY_SCHEDULE,
  queryByVendor: QUERY_BY_VENDOR,
  queryByContract: QUERY_BY_CONTRACT,
};

export default connect(
  state => ({
    selectedSchedule: state.schedule,
    queryBy: state.query_by,
  })
)(SearchCategory);
