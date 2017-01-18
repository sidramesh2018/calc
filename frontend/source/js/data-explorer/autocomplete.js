/* global $ document */

import hourglass from '../common/hourglass';

export function appendHighlightedTerm($el, term, searchStr) {
  const sanitizedSearch = searchStr.replace(/[^a-z0-9 ]/gi, '')
    .trim()
    .split(/[ ]+/)
    .join('|');
  const re = new RegExp(`(${sanitizedSearch})`, 'gi');

  const plainText = (start, end) => document.createTextNode(
    term.substring(start, end),
  );
  const highlightedText = (start, end) => $('<b></b>').text(
    term.substring(start, end),
  )[0];

  let done = false;
  let lastIndex = 0;
  while (!done) {
    const result = re.exec(term);
    if (result === null) {
      $el.append(plainText(lastIndex));
      done = true;
    } else {
      $el.append(plainText(lastIndex, result.index));
      $el.append(highlightedText(result.index, re.lastIndex));
      lastIndex = re.lastIndex;
    }
  }

  return $el;
}

export function destroy(el) {
  $(el).autoComplete('destroy');
}

export function initialize(el, {
  api,
  getQueryType,
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
        const categories = result.slice(0, 20).map(d => ({
          term: d.labor_category,
          count: d.count,
        }));
        return done(categories);
      });
    },
    renderItem(item, searchStr) {
      const term = item.term || item;
      const $div = $('<div class="autocomplete-suggestion"></div>')
        .attr('data-val', term);

      appendHighlightedTerm(
        $('<span class="term"></span>').appendTo($div),
        term,
        searchStr,
      );
      $('<span class="count"></span>').text(item.count.toString())
        .appendTo($div);

      return $('<div></div>').append($div).html();
    },
    onSelect(e, term) {
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
      } else {
        selectedInput = `${term}, `;
      }

      // update the search input field accordingly
      setFieldValue(selectedInput);
    },
  });
}
