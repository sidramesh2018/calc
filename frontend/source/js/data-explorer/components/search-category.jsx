import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Schedule from './schedule';
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
    autobind(this, ['toggleDropdown', 'closeMenuOnClick']);
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

  // TODO: Set up another Redux store to track what choice has been selected
  // Will need to track which schedule has been chosen, or if vendor/contract
  // has been selected.
  render() {
    const { selectedSchedule } = this.props;
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
          <strong>
            Search labor categories
          </strong>
          <span>
            in 
            {' '}
            { scheduleLabels[selectedSchedule] || `${Object.keys(scheduleLabels).length} contract vehicles` }
          </span>
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
          <Schedule />
        </div>
      </div>
    );
  }
}

SearchCategory.propTypes = {
  selectedSchedule: PropTypes.string,
};

SearchCategory.defaultProps = {
  selectedSchedule: '',
};

export default connect(
  state => ({ selectedSchedule: state.schedule })
)(SearchCategory);
