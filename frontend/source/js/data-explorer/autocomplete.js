/* global $ */

import hourglass from '../common/hourglass';

export function destroy(el) {
  $(el).autoComplete('destroy');
}

export function initialize(el, {
  api,
  getQueryType,
  getFieldValue,
  setFieldValue,
}) {
  let autoCompReq;
  let searchTerms = '';

  $(el).autoComplete({
    minChars: 2,
    // delay: 5,
    delay: 0,
    cache: false,
    source(term, done) {
      // save inputted search terms for display later
      searchTerms = term;

      const lastTerm = hourglass.getLastCommaSeparatedTerm(term);

      if (autoCompReq) { autoCompReq.abort(); }
      autoCompReq = api.get({
        uri: 'search/',
        data: {
          q: lastTerm,
          query_type: getQueryType(),
        },
      }, (error, result) => {
        autoCompReq = null;
        if (error) { return done([]); }
        const categories = result.slice(0, 20).map((d) => ({
          term: d.labor_category,
          count: d.count,
        }));
        return done(categories);
      });
    },
    renderItem(item, searchStr) {
      const re = new RegExp(`(${searchStr.split(' ').join('|')})`, 'gi');
      const term = item.term || item;
      return [
        `<div class="autocomplete-suggestion" data-val="${term}">`,
        '<span class="term">', term.replace(re, '<b>$1</b>'), '</span>',
        '<span class="count">', item.count, '</span>',
        '</div>',
      ].join('');
    },
    onSelect(e, term, item, autocompleteSuggestion) {
      let selectedInput;

      // check if search field has terms already
      if (searchTerms.indexOf(',') !== -1) {
        const termSplit = searchTerms.split(', ');
        // remove last typed (incomplete) input
        termSplit.pop();
        // combine existing search terms with new one
        selectedInput = `${termSplit.join(', ')}, ${term}, `;
      // if search field doesn't have terms
      // but has selected an autocomplete suggestion,
      // then just show term and comma delimiter
      } else if (autocompleteSuggestion) {
        selectedInput = `${term}, `;
      } else {
        selectedInput = `${getFieldValue()}, `;
      }

      // update the search input field accordingly
      setFieldValue(selectedInput);
    },
  });
}
