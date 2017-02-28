/* global $ */

import React from 'react';

export default class SlideyPanel extends React.Component {
  componentWillAppear(cb) {
    this.slideDown(cb);
  }

  componentWillEnter(cb) {
    this.slideDown(cb);
  }

  slideDown(cb) {
    if (typeof $ !== 'undefined') {
      $(this.el).hide().slideDown('fast', cb);
    } else {
      cb();
    }
  }

  componentWillLeave(cb) {
    if (typeof $ !== 'undefined') {
      $(this.el).slideUp('fast', cb);
    } else {
      cb();
    }
  }

  render() {
    const newProps = { ref: (el) => { this.el = el; } };

    Object.assign(newProps, this.props);

    delete newProps.children;
    delete newProps.component;

    return React.createElement(
      this.props.component,
      newProps,
      this.props.children,
    );
  }
}

SlideyPanel.propTypes = {
  component: React.PropTypes.any.isRequired,
  children: React.PropTypes.any.isRequired,
};
