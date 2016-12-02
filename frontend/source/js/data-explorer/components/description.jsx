import React from 'react';
import { connect } from 'react-redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  EDU_LABELS,
  SITE_LABELS,
  BUSINESS_SIZE_LABELS,
  SCHEDULE_LABELS,
} from '../constants';

import { formatCommas } from '../util';

function Filter({
  extraClassName,
  label,
  children,
}) {
  let className = 'filter';

  if (extraClassName) {
    className += ` ${extraClassName}`;
  }

  return (
    <span className={className}>
      {label ? `${label}: ` : null}
      <a className="focus-input" href="#">
        {children}
      </a>
    </span>
  );
}

Filter.propTypes = {
  extraClassName: React.PropTypes.string,
  label: React.PropTypes.string,
  children: React.PropTypes.any.isRequired,
};

function Description({
  shownResults,
  totalResults,
  minExperience,
  maxExperience,
  education,
  site,
  businessSize,
  schedule,
  laborCategory,
}) {
  let results = ' results ';
  const filtersClasses = ['filters'];
  const filters = [];

  if (laborCategory) {
    filters.push(<Filter key="lab">{laborCategory}</Filter>);
  }

  if (education.length) {
    filters.push(
      <Filter key="edu" label="education level"
              extraClassName="education-filter">
        {education.map(x => EDU_LABELS[x]).join(', ')}
      </Filter>
    );
  }

  if (minExperience !== MIN_EXPERIENCE ||
      maxExperience !== MAX_EXPERIENCE) {
    filters.push(
      <Filter key="exp" label="experience">
        {minExperience} - {maxExperience} years
      </Filter>
    );
  }

  if (site) {
    filters.push(
      <Filter key="sit" label="worksite">
        {SITE_LABELS[site]}
      </Filter>
    );
  }

  if (businessSize) {
    filters.push(
      <Filter key="bus" label="business size">
        {BUSINESS_SIZE_LABELS[businessSize]}
      </Filter>
    );
  }

  if (schedule) {
    filters.push(
      <Filter key="sch" label="schedule">
        {SCHEDULE_LABELS[schedule]}
      </Filter>
    );
  }

  if (filters.length) {
    results += 'with ';
  } else {
    filtersClasses.push('hidden');
  }

  // TODO: The original version of this faded-in (but never out)
  // whenever it changed. We might want to do that too, or choose
  // a different animation.

  // TODO: The original version of this didn't show the filters on
  // the very first request (it also kept track of how many requests
  // had been made) but I'm not sure why that was good for usability,
  // so I've left the functionality out for now. We can bring it back
  // if needed.

  return (
    <p className="">
      {`Showing ${formatCommas(shownResults)} of `}
      <span className="total">{formatCommas(totalResults)}</span>
      {results}
      <span className={filtersClasses.join(' ')}>
        {filters}
      </span>
    </p>
  );
}

Description.propTypes = {
  shownResults: React.PropTypes.number.isRequired,
  totalResults: React.PropTypes.number.isRequired,
  minExperience: React.PropTypes.number.isRequired,
  maxExperience: React.PropTypes.number.isRequired,
  education: React.PropTypes.array.isRequired,
  site: React.PropTypes.string.isRequired,
  businessSize: React.PropTypes.string.isRequired,
  schedule: React.PropTypes.string.isRequired,
  laborCategory: React.PropTypes.string.isRequired,
};

function mapStateToProps(state) {
  return {
    shownResults: state.rates.data.results.length,
    totalResults: state.rates.data.count,
    minExperience: state.min_experience,
    maxExperience: state.max_experience,
    education: state.education,
    site: state.site,
    businessSize: state.business_size,
    schedule: state.schedule,
    laborCategory: state.q,
  };
}

export default connect(mapStateToProps)(Description);
