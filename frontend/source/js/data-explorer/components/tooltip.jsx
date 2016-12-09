/* global $ */

import React from 'react';

export default class Tooltip extends React.Component {
  componentDidMount() {
    $(this.el)
      .tooltipster({})
      .tooltipster('content', this.props.text);
  }

  componentDidUpdate(prevProps) {
    if (this.props.text !== prevProps.text) {
      $(this.el).tooltipster('content', this.props.text);
    }
  }

  componentWillUnmount() {
    $(this.el).tooltipster('destroy');
  }

  render() {
    return (
      <span ref={(el) => { this.el = el; }}>
        {this.props.children}
      </span>
    );
  }
}

Tooltip.propTypes = {
  children: React.PropTypes.any,
  text: React.PropTypes.string.isRequired,
};
