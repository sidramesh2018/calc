import React from 'react';

import createSortableColumn from './sortable-column';

const column = createSortableColumn('labor_category');

export const HeaderCell = column.connectHeaderCell(
  ({ className, toggleSort }) => (
    <th scope="col"
        className={className}
        onClick={toggleSort}>
      Labor Category
    </th>
  )
);

export const DataCell = column.connectDataCell(
  ({ className, result }) => (
    <th className={className} scope="row">
      {result.labor_category}
    </th>
  )
);

export const [boop, jones] = [1, 2];
