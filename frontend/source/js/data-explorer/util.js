/* global event */

import classNames from 'classnames';
import { format } from 'd3-format';
import { csvFormatRows, csvParseRows } from 'd3-dsv';

export const formatCommas = format(',');
export const formatPrice = format(',.0f');
export const formatPriceWithCents = format(',.02f');
export const formatFriendlyPrice = (price) => {
  if (Math.floor(price) === price) {
    return formatPrice(price);
  }
  return formatPriceWithCents(price);
};

const KEY_ENTER = 13;
const KEY_SPACE = 32;

export function handleEnter(cb) {
  return (event) => {
    if (event.keyCode === KEY_ENTER) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function handleEnterOrSpace(cb) {
  return (event) => {
    if (event.keyCode === KEY_ENTER || event.keyCode === KEY_SPACE) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function autobind(self, names) {
  const target = self;

  names.forEach((name) => {
    target[name] = target[name].bind(target);
  });
}

export function templatize(str, undef) {
  const undefFunc = () => undef;
  return d => str.replace(/{(\w+)}/g, (_, key) => d[key] || undefFunc.call(d, key));
}

export function parsePrice(value, defaultValue = 0) {
  let floatValue = parseFloat(value);

  if (isNaN(floatValue) || floatValue < 0) {
    floatValue = defaultValue;
  }

  return floatValue;
}

// http://stackoverflow.com/a/13419367
export function parseQuery(qstr) {
  const query = {};
  const a = qstr.substr(1).split('&');

  for (let i = 0; i < a.length; i++) {
    const b = a[i].split('=');
    query[decodeURIComponent(b[0])] = decodeURIComponent(
      (b[1] || '').replace(/\+/g, ' '),
    );
  }

  return query;
}

export function joinQuery(query) {
  const parts = Object.keys(query).map((name) => {
    const encName = encodeURIComponent(name);
    const encValue = encodeURIComponent(query[name]);

    return `${encName}=${encValue}`;
  }).join('&');

  return `?${parts}`;
}

export function filterActive(isActive, otherClasses = '') {
  return classNames(isActive ? 'filter_active' : '', otherClasses);
}

export function getLastCommaSeparatedTerm(term) {
  const pieces = term.split(/\s*,\s*/);
  return pieces[pieces.length - 1];
}

export function stripTrailingComma(str) {
  // Removes trailing comma and whitespace from given string
  return str.replace(/,\s*$/, '');
}

export function queryStringToValuesArray(query) {
  if (!query || query.trim().length === 0) {
    return null;
  }
  const values = csvParseRows(query)[0]
    .map(s => ({ name: s.trim() }))
    .filter(v => v.name.length !== 0);

  return values.length ? values : null;
}

export function valuesArrayToQueryString(values) {
  if (!values) {
    return '';
  }
  const names = values
    .map(v => v.name)
    .filter(n => !!n);
  return csvFormatRows([names]);
}
