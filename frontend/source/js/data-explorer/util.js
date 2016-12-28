/* global event */

import classNames from 'classnames';
import { format } from 'd3-format';

export const formatCommas = format(',');
export const formatPrice = format(',.0f');
export const formatPriceWithCents = format(',.02f');

const KEY_ENTER = 13;
const KEY_SPACE = 32;

export function handleEnter(cb) {
  return event => {
    if (event.keyCode === KEY_ENTER) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function handleEnterOrSpace(cb) {
  return event => {
    if (event.keyCode === KEY_ENTER || event.keyCode === KEY_SPACE) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function autobind(self, names) {
  const target = self;

  names.forEach(name => {
    target[name] = target[name].bind(target);
  });
}

export function templatize(str, undef) {
  const undefFunc = () => undef;
  return (d) => str.replace(/{(\w+)}/g, (_, key) => d[key] || undefFunc.call(d, key));
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
      (b[1] || '').replace(/\+/g, ' ')
    );
  }

  return query;
}

export function joinQuery(query) {
  const parts = Object.keys(query).map(name => {
    const encName = encodeURIComponent(name);
    const encValue = encodeURIComponent(query[name]);

    return `${encName}=${encValue}`;
  }).join('&');

  return `?${parts}`;
}

export function filterActive(isActive, otherClasses = '') {
  return classNames(isActive ? 'filter_active' : '', otherClasses);
}
