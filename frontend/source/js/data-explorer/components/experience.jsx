/* global $ */

import React from 'react';
import { connect } from 'react-redux';

import {
  setExperience,
} from '../actions';

import {
  autobind,
  filterActive,
} from '../util';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
} from '../constants';

export class Experience extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['onSliderSlide', 'onSliderChange']);
    this.state = {
      isSliding: false,
      sliderVal: null,
    };
  }

  componentDidMount() {
    // We're currently using an old version of noUiSlider (7.0.10). Its
    // documentation can only be seen via archive.org:
    //
    // https://web.archive.org/web/20141224210103/http://refreshless.com/nouislider/

    $(this.sliderEl).noUiSlider({
      start: [
        this.props.min,
        this.props.max,
      ],
      step: 1,
      connect: true,
      range: {
        min: MIN_EXPERIENCE,
        max: MAX_EXPERIENCE,
      },
    });
    $(this.sliderEl).on({
      slide: this.onSliderSlide,
      change: this.onSliderChange,
    });
  }

  componentDidUpdate() {
    if (!this.state.isSliding) {
      const [min, max] = this.getSliderVal();

      if (min !== this.props.min || max !== this.props.max) {
        $(this.sliderEl).val([this.props.min, this.props.max]);
      }
    }
  }

  getSliderVal() {
    return $(this.sliderEl).val().map(x => parseInt(x, 10));
  }

  onSliderSlide() {
    $('.noUi-horizontal .noUi-handle', this.rootEl).addClass('filter_focus');

    this.setState({
      isSliding: true,
      sliderVal: this.getSliderVal(),
    });
  }

  onSliderChange() {
    $('.noUi-horizontal .noUi-handle', this.rootEl)
      .removeClass('filter_focus');

    const [min, max] = this.getSliderVal();

    this.setState({
      isSliding: false,
      sliderVal: null,
    });

    if (min !== this.props.min) {
      this.props.setExperience('min', min);
    }
    if (max !== this.props.max) {
      this.props.setExperience('max', max);
    }
  }

  makeOptions(min, max) {
    const options = [];

    for (let i = min; i <= max; i++) {
      options.push(<option key={i} value={i}>{i}</option>);
    }

    return options;
  }

  render() {
    let min = this.props.min;
    let max = this.props.max;

    if (this.state.isSliding) {
      [min, max] = this.state.sliderVal;
    }

    const minId = `${this.props.idPrefix}min`;
    const maxId = `${this.props.idPrefix}max`;
    const baseClasses = 'select-small';
    const minClasses = filterActive(min !== MIN_EXPERIENCE, baseClasses);
    const maxClasses = filterActive(max !== MAX_EXPERIENCE, baseClasses);

    const onChange = type => e => {
      this.props.setExperience(type, parseInt(e.target.value, 10));
    };

    return (
      <div className="filter" ref={(el) => { this.rootEl = el; }}>
        <fieldset>
          <legend>
            Experience:
          </legend>
          <div className="slider" ref={(el) => { this.sliderEl = el; }} />
          <div className="experience_range">
            <label htmlFor={minId} className="sr-only">Minimum Years</label>
            <select id={minId} value={min} name="min_experience"
                    onChange={onChange('min')}
                    className={minClasses}>
              {this.makeOptions(MIN_EXPERIENCE, max)}
            </select>
            {' - '}
            <label htmlFor={maxId} className="sr-only">Maximum Years</label>
            <select id={maxId} value={max} name="max_experience"
                    onChange={onChange('max')}
                    className={maxClasses}>
              {this.makeOptions(min, MAX_EXPERIENCE)}
            </select>
            {' years'}
          </div>
        </fieldset>
      </div>
    );
  }
}

Experience.propTypes = {
  min: React.PropTypes.number.isRequired,
  max: React.PropTypes.number.isRequired,
  setExperience: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string,
};

Experience.defaultProps = {
  idPrefix: 'experience-',
};

export default connect(
  state => ({
    min: state.min_experience,
    max: state.max_experience,
  }),
  { setExperience }
)(Experience);
