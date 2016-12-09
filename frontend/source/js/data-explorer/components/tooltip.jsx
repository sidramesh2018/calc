/* global $ */

import React from 'react';

import { autobind } from '../util';

export default class Tooltip extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['show', 'hide']);
  }

  componentDidMount() {
    $(this.el)
      .tooltipster({})
      .tooltipster('content', this.props.text);
    this.el.addEventListener('focus', this.show, true);
    this.el.addEventListener('blur', this.hide, true);
  }

  componentDidUpdate(prevProps) {
    if (this.props.text !== prevProps.text) {
      $(this.el).tooltipster('content', this.props.text);
    }
  }

  componentWillUnmount() {
    $(this.el).tooltipster('destroy');
    this.el.removeEventListener('focus', this.show, true);
    this.el.removeEventListener('blur', this.hide, true);
  }

  show() {
    $(this.el).tooltipster('show');
  }

  hide() {
    $(this.el).tooltipster('hide');
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
