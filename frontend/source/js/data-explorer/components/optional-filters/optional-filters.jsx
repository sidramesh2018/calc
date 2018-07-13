import React, { Fragment } from 'react';

import BusinessSize from '../business-size';
import EducationLevel from '../education-level';
import Experience from '../experience';
import Site from '../site';

const OptionalFilters = () => (
  <Fragment>
    <EducationLevel />
    <Experience />
    <Site />
    <BusinessSize />
  </Fragment>
);

export default OptionalFilters;
