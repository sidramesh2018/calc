import React from 'react';
import classNames from 'classnames';

import createSortableColumn from './sortable-column';

const column = createSortableColumn('labor_category');

export const HeaderCell = column.connectHeaderCell(
  ({ toggleSort, baseClasses }) => (
    <th scope="col"
        className={classNames(baseClasses)}
        onClick={toggleSort}>
      Labor Category
    </th>
  )
);

export const DataCell = column.connectDataCell(
  ({ baseClasses, result }) => (
    <th className={classNames(baseClasses)} scope="row">
      {result.labor_category}
    </th>
  )
);
