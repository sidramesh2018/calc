import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Schedule from './schedule';
import { scheduleLabels } from '../schedule-metadata';

import {
  autobind,
  handleEnterOrSpace,
} from '../util';

function elementContains(container, contained) {
  let target = contained.parentNode;

  while (target) {
    if (target === container) {
      return true;
    }
    target = target.parentNode;
  }
  return false;
}

export class SearchCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
    };
    autobind(this, ['handleDocumentClick', 'toggleDropdown']);
  }


  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);
  }

  componentWillUnmount() {
    document.removeEventListener('click', this.handleDocumentClick);
    document.removeEventListener('focus', this.handleDocumentClick, true);
  }

  handleDocumentClick(e) {
    if (!this.state.expanded) {
      return;
    }

    // Whenever users click outside of our dropdown, hide it.
    if (!elementContains(this.dropdownEl, e.target)) {
      this.setState({ expanded: false });
    }
  }

  toggleDropdown(e) {
    this.setState({
      expanded: !this.state.expanded, /* eslint-disable-line react/no-access-state-in-setstate */
    });
    console.log(this.state);
  }

  // TODO: Set up another Redux store to track what choice has been selected
  // Will need to track which schedule has been chosen, or if vendor/contract
  // has been selected.
  render() {
    const { selectedSchedule } = this.props;
    return (
      <div
        className="html-dropdown"
        ref={(el) => { this.dropdownEl = el; }}
      >
        <button
          className="html-dropdown__trigger"
          aria-controls="data-explorer__search-category"
          onClick={this.toggleDropdown}
          aria-expanded={this.state.expanded}
         >
          <strong>
            Search labor categories
          </strong>
          <span>
            in { scheduleLabels[selectedSchedule] || `${Object.keys(scheduleLabels).length} contract vehicles` }
          </span>
        </button>
        <div
          className="html-dropdown__choices"
          id="data-explorer__search-category"
          onClick={this.toggleDropdown}
          aria-hidden={!this.state.expanded}
         >
          <Schedule />
        </div>
      </div>
    );
  }
}

export default connect(
  state => ({ selectedSchedule: state.schedule })
)(SearchCategory);
