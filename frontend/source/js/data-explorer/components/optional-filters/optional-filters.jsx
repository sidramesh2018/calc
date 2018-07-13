import React, { Fragment } from 'react';

import BusinessSize from '../business-size';
import EducationLevel from '../education-level';
import Experience from '../experience';
import Site from '../site';

const OptionalFilters = () => (
  <Fragment>
    <div className="row">
      <div className="columns three">
        <EducationLevel />
      </div>
      <div className="columns three">
        <Experience />
      </div>
      <div className="columns three">
        <Site />
      </div>
      <div className="columns three">
        <BusinessSize />
      </div>
    </div>
  </Fragment>
);

export default OptionalFilters;
