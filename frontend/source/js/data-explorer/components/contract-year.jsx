import React from 'react';
import { connect } from 'react-redux';

import Tooltip from './tooltip';
import { setContractYear as setContractYearAction } from '../actions';
import {
  CONTRACT_YEAR_CURRENT,
  CONTRACT_YEAR_1,
  CONTRACT_YEAR_2,
  CONTRACT_YEAR_LABELS,
} from '../constants';

function ContractYear({ idPrefix, contractYear, setContractYear }) {
  const idCurrent = `${idPrefix}current-year`;
  const id1 = `${idPrefix}one-year-out`;
  const id2 = `${idPrefix}two-years-out`;
  const setYear = year => () => { setContractYear(year); };

  return (
    <div className="filter contract-year">
      <fieldset className="fieldset-inputs">

        <legend>Contract year:</legend>
        <a href="#" className="tooltip filter-more-info">
           <Tooltip text="All five years of pricing are available in the export">
             What's this?
           </Tooltip>
        </a>
        <h3 className="sr-only">Contract Year</h3>

        <ul className="contract-year-block">
          <li className="contract-list-item">
            <label htmlFor={idCurrent} className="radio">
              <input id={idCurrent} type="radio"
                     checked={contractYear === CONTRACT_YEAR_CURRENT}
                     onChange={setYear(CONTRACT_YEAR_CURRENT)}
                     name="contract-year" value={CONTRACT_YEAR_CURRENT}
                     tabIndex="0" />
              <span tabIndex="-1"
                    className="contract-current-year-span checkbox-focus"
                    aria-hidden="true">Current</span>
              <span className="sr-only">
                {CONTRACT_YEAR_LABELS[CONTRACT_YEAR_CURRENT]}
              </span>
            </label>
          </li>
          <li className="contract-list-item">
            <label htmlFor={id1} className="radio">
              <input id={id1} type="radio"
                     checked={contractYear === CONTRACT_YEAR_1}
                     onChange={setYear(CONTRACT_YEAR_1)}
                     name="contract-year" value={CONTRACT_YEAR_1}
                     tabIndex="0" />
              <span tabIndex="-1"
                    className="checkbox-focus"
                    aria-hidden="true">+1</span>
              <span className="sr-only">
                {CONTRACT_YEAR_LABELS[CONTRACT_YEAR_1]}
              </span>
            </label>
          </li>
          <li className="contract-list-item">
            <label htmlFor={id2} className="radio">
              <input id={id2} type="radio"
                     name="contract-year" value={CONTRACT_YEAR_2}
                     checked={contractYear === CONTRACT_YEAR_2}
                     onChange={setYear(CONTRACT_YEAR_2)}
                     tabIndex="0" />
              <span tabIndex="-1"
                    className="contract-last-year-span checkbox-focus"
                    aria-hidden="true">+2</span>
              <span className="sr-only">
                {CONTRACT_YEAR_LABELS[CONTRACT_YEAR_2]}
              </span>
            </label>
          </li>
        </ul>
      </fieldset>
    </div>
  );
}

ContractYear.propTypes = {
  contractYear: React.PropTypes.string.isRequired,
  setContractYear: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string,
};

ContractYear.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ contractYear: state['contract-year'] }),
  { setContractYear: setContractYearAction }
)(ContractYear);
