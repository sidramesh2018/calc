// We're eventually going to add more exports here, so for
// now we want to suppress eslint's warning to prefer a default
// export.

/* eslint import/prefer-default-export: 0 */

import React from 'react';

export function makeOptions(labels) {
  return [
    { key: '', value: '', label: '(all)' },
  ].concat(Object.keys(labels).map(
    value => ({ value, label: labels[value] }),
  )).map(({ value, label }) => (
    <option key={value} value={value}>{label}</option>
  ));
}
