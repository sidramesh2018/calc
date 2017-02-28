/* global window */

import React from 'react';

export default class SlideyPanel extends React.Component {
  componentWillAppear(cb) {
    this.slideDown(cb);
  }

  componentWillEnter(cb) {
    this.slideDown(cb);
  }

  slideDown(cb) {
    this.props.$(this.el).hide().slideDown('fast', cb);
  }

  componentWillLeave(cb) {
    this.props.$(this.el).slideUp('fast', cb);
  }

  render() {
    const newProps = { ref: (el) => { this.el = el; } };

    Object.assign(newProps, this.props);

    delete newProps.children;
    delete newProps.component;
    delete newProps.$;

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
  $: React.PropTypes.func,
};

SlideyPanel.defaultProps = {
  $: window.$ || function fakeJquery() {
    return {
      hide() { return this; },
      slideUp(speed, cb) { cb(); },
      slideDown(speed, cb) { cb(); },
    };
  },
};
