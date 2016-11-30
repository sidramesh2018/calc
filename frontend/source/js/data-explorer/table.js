/* global $, d3, document */

import {
  formatCommas,
  getFormat,
} from './util';

import { store, excludeRow } from './store';

const RESULTS_TABLE = '#results-table';
const RESULTS_COUNT = '#results-count';

const resultsTable = d3.select(RESULTS_TABLE).style('display', 'none');
const sortHeaders = resultsTable.selectAll('thead th');

function parseSortOrder(order) {
  if (!order) {
    return { key: null, order: null };
  }
  const first = order.charAt(0);
  const sort = { order: '' };
  switch (first) {
    case '-':
      sort.order = first;
      order = order.substr(1); // eslint-disable-line no-param-reassign
      break;
    default:
      break;
  }
  sort.key = order;
  return sort;
}

export function updateResults(form, data) {
  const results = data.results;
  d3.select(RESULTS_COUNT)
    .text(formatCommas(data.count));

  resultsTable.style('display', null);

  const thead = resultsTable.select('thead');
  const columns = thead.selectAll('th').data();
  const tbody = resultsTable.select('tbody');

  const tr = tbody.selectAll('tr')
    .data(results);

  tr.exit().remove();

  tr.enter().append('tr')
  .on('mouseover', function onMouseover() {
    const label = this.querySelector('.years');
    label.className = label.className.replace('hidden', '');
  })
  .on('mouseout', function onMouseout() {
    const label = this.querySelector('.years');
    label.className = `${label.className} hidden`;
  });

  const td = tr.selectAll('.cell')
    .data((d) => columns.map((column) => {
      const key = column.key;
      const priceFields = ['current_price', 'next_year_price', 'second_year_price'];
      let value = d[key];
      let yearField;

        // check if we need to be loading a future price
        // and, if so, the price value should reflect the filter choice
      if (column.key === 'current_price') {
        yearField = form.getData()['contract-year'];
        if (!isNaN(yearField)) {
          value = d[priceFields[yearField]];
        }
      }

      return {
        column,
        row: d,
        key,
        value,
        string: column.format(value),
      };
    }));

  td.exit().remove();

  const sortKey = parseSortOrder(form.getData().sort).key;

  const enter = td.enter()
      .append((d) => {
        const name = d.column.key === 'labor_category' ? 'th' : 'td';
        return document.createElement(name);
      })
      .attr('class', (d) => `cell column-${d.key}`)
      .classed('collapsed', (d) => d.column.collapsed)
      .classed('sorted', (c) => c.column.key === sortKey);

  enter.filter(function isTh() { return this.nodeName === 'TH'; })
    .attr('scope', 'row');

  // update the HTML of all cells (except exclusion columns)
  td.filter((d) => d.key !== 'exclude')
  .html((d) => {
    // don't just do "if !(d.string)" because 0 is valid
    if (d.string === null) {
      d.string = 'N/A'; // eslint-disable-line no-param-reassign
    }

    return d.column.collapsed ? '' : d.string;
  });

  // add "years" the experience number, shown on row hover
  td.filter((d) => d.key === 'min_years_experience')
  .html((d) => {
    const label = d.string === 1 ? 'year' : 'years';
    return `${d.string} <span class="years hidden">${label}</span>`;
  });

  // add links to contracts
  td.filter((d) => d.key === 'idv_piid')
  .html((d) => {
    const id = d.string.split('-').join('');
    return `<a target="_blank" href="https://www.gsaadvantage.gov/ref_text/${id}/${id}_online.htm">` +
      `${d.string}<svg class="document-icon" width="8" height="8" viewBox="0 0 8 8">` +
      '<path d="M0 0v8h7v-4h-4v-4h-3zm4 0v3h3l-3-3zm-3 ' +
      '2h1v1h-1v-1zm0 2h1v1h-1v-1zm0 2h4v1h-4v-1z" />' +
      '</svg>';
  });

  // add a link to incoming exclusion cells
  enter.filter((d) => d.key === 'exclude')
  .append('a')
    .attr('class', 'exclude-row')
    .html('&times;')
    .each(function enableTooltipster() {
      $(this).tooltipster({
        position: 'bottom',
      });
    });


  // update the links on all exclude cells
  td.filter((d) => d.key === 'exclude')
  .select('a')
    .attr('href', (d) => `?exclude=${d.row.id}`)
    .attr('aria-label', (d) => `Exclude ${d.row.labor_category} from your search`)
    .each(function setTooltipsterContent() {
      $(this).tooltipster('content', this.getAttribute('aria-label'));
    })

    .on('click', function onClick(d) {
      d3.event.preventDefault();
      /*
       * XXX this is where d3.select(this).parent('tr')
       * would be nice...
       */
      const parentTr = this.parentNode.parentNode;
      parentTr.parentNode.removeChild(parentTr);

      store.dispatch(excludeRow(d.row.id));
    });
}

function updateSortOrder(key) {
  const title = (d) => {
    if (d.sorted) {
      const order = d.descending ? 'descending' : 'ascending';
      const other = d.descending ? 'ascending' : 'descending';
      return [d.title, ': sorted ', order, ', select to sort ', other].join('');
    }
    // else
    return `${d.title}: select to sort ascending`;
  };

  sortHeaders
    .filter((d) => d.sortable)
      .classed('sorted', (c) => c.sorted)
      .classed('ascending', (c) => c.sorted && !c.descending)
      .classed('descending', (c) => c.sorted && c.descending)
      .attr('aria-label', title)
      .each(function setTooltipsterContent() {
        $(this).tooltipster('content', this.getAttribute('aria-label'));
      });

  resultsTable.selectAll('tbody td')
    .classed('sorted', (c) => c.column.key === key);
}

function setupSortHeaders(form, submit, headers) {
  function setSortOrder(d, i) {
    headers.each((c, j) => {
      if (j !== i) {
        c.sorted = false; // eslint-disable-line no-param-reassign
        c.descending = false; // eslint-disable-line no-param-reassign
      }
    });

    if (d.sorted) {
      d.descending = !d.descending; // eslint-disable-line no-param-reassign
    }
    d.sorted = true; // eslint-disable-line no-param-reassign

    const sort = (d.descending ? '-' : '') + d.key;
    form.set('sort', sort);

    updateSortOrder(d.key);

    submit(true);
  }

  headers
    .each((d) => {
      d.sorted = false; // eslint-disable-line no-param-reassign
      d.descending = false; // eslint-disable-line no-param-reassign
    })
    .attr('tabindex', 0)
    .attr('aria-role', 'button')
    .on('click.sort', setSortOrder);
}

export function setupColumnHeader(form, submit, headers) {
  headers
    .datum(function setupDatum() {
      return {
        key: this.getAttribute('data-key'),
        title: this.getAttribute('title') || this.textContent,
        format: getFormat(this.getAttribute('data-format')),
        sortable: this.classList.contains('sortable'),
        collapsible: this.classList.contains('collapsible'),
      };
    })
    .each(function addClass(d) {
      this.classList.add(`column-${d.key}`);
    });

  // removed temporarily to prevent collision with tooltips [TS]
  // headers.filter(function(d) { return d.collapsible; })
  //   .call(setupCollapsibleHeaders);

  headers.filter((d) => d.sortable)
    .call(setupSortHeaders.bind(this, form, submit));
}

export function initializeTable(form, submit) {
  sortHeaders.call(setupColumnHeader.bind(this, form, submit));
}

export function updateSort(unparsedSortData) {
  const sort = parseSortOrder(unparsedSortData);
  const sortable = (d) => d.sortable;
  sortHeaders
    .filter(sortable)
    .classed('sorted', (d) => {
      d.sorted = (d.key === sort.key); // eslint-disable-line no-param-reassign
    })
    .classed('descending', (d) => {
      d.descending = (d.sorted && sort.order === '-'); // eslint-disable-line no-param-reassign
    });

  updateSortOrder(sort.key);
}
