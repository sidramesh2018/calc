/* global document */

import React from 'react';
import { connect } from 'react-redux';

import {
  autobind,
  handleEnterOrSpace,
} from '../util';

import {
  EDU_LABELS,
} from '../constants';

import {
  toggleEducationLevel,
} from '../actions';

// TODO: We could just use jQuery for this, but I wanted to decouple
// the new React code from jQuery as much as possible for now.
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

/**
 * The following logic was created to mimic the following
 * legacy jQuery behavior:
 *
 *   Dropdown with Multiple checkbox select with jQuery - May 27, 2013
 *   (c) 2013 @ElmahdiMahmoud
 *   license: http://www.opensource.org/licenses/mit-license.php
 */

class EducationLevel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
    };
    autobind(this, ['handleToggleMenu', 'handleDocumentClick']);
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

  handleToggleMenu(e) {
    // TODO: The original jQuery logic used .slideDown() here, it'd
    // be nice if we could use some sort of transition too.

    e.preventDefault();
    this.setState({
      expanded: !this.state.expanded,
    });
  }

  handleCheckboxClick(level) {
    this.props.toggleEducationLevel(level);
  }

  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);
  }

  componentWillUnmount() {
    document.removeEventListener('click', this.handleDocumentClick);
    document.removeEventListener('focus', this.handleDocumentClick, true);
  }

  render() {
    const levels = this.props.levels;
    const idPrefix = this.props.idPrefix;
    const ddStyle = this.state.expanded ? { display: 'block' } : null;
    const inputs = Object.keys(EDU_LABELS).map(value => {
      const id = idPrefix + value;

      return (
        <li key={value}>
          <input
            id={id}
            type="checkbox"
            value={value}
            checked={levels.indexOf(value) >= 0}
            onChange={this.handleCheckboxClick.bind(this, value)}
            name="education" />
          <label htmlFor={id}>{EDU_LABELS[value]}</label>
        </li>
      );
    });
    let linkContent;

    if (levels.length === 0) {
      linkContent = (
        <span className="eduSelect">Select
          <span className="sr-only"> to reveal Education Level options</span>
        </span>
      );
    } else {
      const selectedLevels = levels.map(value => {
        const label = EDU_LABELS[value];
        return <span key={value} title={label}>{label}</span>;
      });
      linkContent = (
        <div className="multiSel">{selectedLevels}</div>
      );
    }

    return (
      <div>
        <label>Education level:</label>
        <dl className="dropdown"
            ref={(el) => { this.dropdownEl = el; } }>
          <dt>
            <a href="#" onClick={this.handleToggleMenu}
               role="button"
               aria-expanded={this.state.expanded.toString()}
               onKeyDown={handleEnterOrSpace(this.handleToggleMenu)}
               className={levels.length === 0 ? '' : 'filter_active'}>
              {linkContent}
            </a>
          </dt>

          <dd>
            <div className="multiSelect">
              <fieldset>
                <legend className="sr-only">Education level:</legend>
                <ul style={ddStyle}>
                  {inputs}
                </ul>
              </fieldset>
            </div>
          </dd>
        </dl>
      </div>
    );
  }
}

EducationLevel.propTypes = {
  levels: React.PropTypes.array.isRequired,
  idPrefix: React.PropTypes.string,
  toggleEducationLevel: React.PropTypes.func.isRequired,
};

EducationLevel.defaultProps = {
  idPrefix: 'education-level-',
};

export default connect(
  state => ({ levels: state.education }),
  { toggleEducationLevel }
)(EducationLevel);
