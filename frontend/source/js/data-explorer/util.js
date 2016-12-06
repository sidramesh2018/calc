/* global window, d3, event */

// for IE9: History API polyfill
export const location = window.history.location || window.location;
// TODO: if location.hash, read that
// e.g. if an IE9 user sends a link to a Chrome user, they should see the
// same stuff.

export const formatCommas = d3.format(',');
export const formatPrice = d3.format(',.0f');

export function autobind(self, names) {
  const target = self;

  names.forEach(name => {
    target[name] = target[name].bind(target);
  });
}

export function templatize(str, undef) {
  const undefFunc = d3.functor(undef);
  return (d) => str.replace(/{(\w+)}/g, (_, key) => d[key] || undefFunc.call(d, key));
}

export function getFormat(spec) {
  if (!spec) {
    return (d) => d;
  }

  const index = spec.indexOf('%');
  if (index === -1) {
    return d3.format(spec);
  }
  const prefix = spec.substr(0, index);
  const format = d3.format(spec.substr(index + 1));
  return (str) => {
    if (!str) {
      return '';
    }
    return prefix + format(+str);
  };
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
    query[decodeURIComponent(b[0])] = decodeURIComponent(b[1] || '');
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
