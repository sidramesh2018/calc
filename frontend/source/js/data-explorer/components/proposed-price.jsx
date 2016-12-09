import React from 'react';
import { connect } from 'react-redux';

import { setProposedPrice } from '../actions';

class ProposedPrice extends React.Component {
  constructor(props) {
    super(props);
    this.state = { typed: this.props.proposedPrice || '' };
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(e) {
    const value = e.target.value;
    const filteredChars = [];
    let decimalFound = false;
    let centDigits = 0;

    for (let i = 0; i < value.length; i++) {
      const c = value[i];

      if (/[0-9]/.test(c) && centDigits < 2) {
        filteredChars.push(c);
        if (decimalFound) {
          centDigits++;
        }
      } else if (c === '.' && !decimalFound) {
        filteredChars.push(c);
        decimalFound = true;
      }
    }

    this.setState({ typed: filteredChars.join('') });
  }

  componentDidUpdate(_, prevState) {
    if (prevState.typed !== this.state.typed) {
      const value = this.state.typed;
      const floatValue = value ? parseFloat(value) : 0;
      if (!isNaN(floatValue) && floatValue >= 0) {
        this.props.dispatch(setProposedPrice(floatValue));
      }
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.proposedPrice !== this.props.proposedPrice) {
      const typedFloat = parseFloat(this.state.typed || '0');
      if (typedFloat !== nextProps.proposedPrice) {
        this.setState({ typed: nextProps.proposedPrice || '' });
      }
    }
  }

  render() {
    // Note that Chrome has issues with number input, so we're just
    // going to use a standard text field here. This is unfortunate for
    // mobile users, since they won't get a numeric keypad.
    //
    // See more details at: https://github.com/facebook/react/issues/1549

    const id = `${this.props.idPrefix}proposed-price`;

    return (
      <div className="proposed-price">
        <label htmlFor={id} className="sr-only">Proposed price</label>
        <input id={id} type="text" name="proposed-price"
               placeholder="Proposed price" value={this.state.typed}
               onChange={this.handleChange} />
        <button className="button-primary go">Go</button>
      </div>
    );
  }
}

ProposedPrice.propTypes = {
  proposedPrice: React.PropTypes.number.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string,
};

ProposedPrice.defaultProps = {
  idPrefix: '',
};

function mapStateToProps(state) {
  return {
    proposedPrice: state['proposed-price'],
  };
}

export default connect(mapStateToProps)(ProposedPrice);
