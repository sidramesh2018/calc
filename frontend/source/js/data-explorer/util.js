/* global window, d3, event */

// for IE9: History API polyfill
export const location = window.history.location || window.location;
// TODO: if location.hash, read that
// e.g. if an IE9 user sends a link to a Chrome user, they should see the
// same stuff.

export const formatCommas = d3.format(',');
export const formatPrice = d3.format(',.0f');

export function getUrlParameterByName(name) {
  const cleanedName = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp(`[\\?&]${cleanedName}=([^&#]*)`);
  const results = regex.exec(location.search);
  return results === null ? ''
    : decodeURIComponent(results[1].replace(/\+/g, ' ')).replace(/[<>]/g, '');
}

export function arrayToCSV(data) {
  // turns any array input data into a comma separated string
  // in use for the education filter
  Object.keys(data).forEach((k) => {
    if (Array.isArray(data[k])) {
      data[k] = data[k].join(','); // eslint-disable-line no-param-reassign
    }
  });

  return data;
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
