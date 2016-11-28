/* global $, window, document, history,
  d3, formdb, XMLSerializer, canvg, wNumb, saveAs, Image, vex */

// wNumb is from nouislider
// saveAs is from FileSaver.js
// canvg is from canvg.js
// vex is from vex.combined.min.js

import ga from '../common/ga';

import hourglass from '../common/hourglass';

import {
  location,
  getUrlParameterByName,
  parseSortOrder,
  arrayToCSV,
  templatize,
  getFormat,
  formatCommas,
  isNumberOrPeriodKey,
} from './util';

import {
  updateExcluded,
  updateResults,
  updateSortOrder,
  sortHeaders,
} from './table';

const MAX_EXPERIENCE = 45;
const HISTOGRAM_BINS = 12;
const search = d3.select('#search');
const form = new formdb.Form(search.node());
const inputs = search.selectAll('*[name]');
const formatPrice = d3.format(',.0f');
const api = new hourglass.API();
const loadingIndicator = search.select('.loading-indicator');
const histogramDownloadLink = document.getElementById('download-histogram');
const EMPTY_DATA = {
  minimum: 0,
  maximum: 0.001,
  average: 0,
  count: 0,
  proposedPrice: 0,
  results: [],
  wage_histogram: [
    { count: 0, min: 0, max: 0 },
  ],
};

let request;
let updateCounter = 0;
let histogramUpdated = false;

function updateDescription(res) {
  const data = form.getData();
  const filters = $('.filters');
  const laborCategoryValue = $('#labor_category').val();
  const lookup = {
    education: {
      label: 'education level',
      html: $('.multiSel').html(),
    },
    min_experience: {
      label: 'experience',
      html: `${$('#min_experience option:selected').text()} - ` +
            `${$('#max_experience option:selected').text()} years`,
    },
    site: {
      label: 'worksite',
      html: $('.filter-site option:selected').text(),
    },
    business_size: {
      label: 'business size',
      html: $('.filter-business_size option:selected').text(),
    },
    schedule: {
      label: 'schedule',
      html: $('.filter-schedule option:selected').text(),
    },
  };

  if (updateCounter) {
    filters.empty().removeClass('hidden').append('with ');
  }

  // fade effect for transitions during description update
  $('#description').hide().fadeIn();

  // first count of results
  d3.select('#description-count')
    .text(formatCommas(res.results.length));

  // labor category results
  if (laborCategoryValue) {
    const laborEl = $(document.createElement('span')).addClass('filter');
    filters.append(laborEl);
    laborEl.append(
      $(document.createElement('a')).addClass('focus-input').attr('href', '#')
        .html(laborCategoryValue)
    );
  }

  Object.keys(data).forEach((dataKey) => {
    if (lookup[dataKey]) {
      // create a span element filter label
      const filterEl = $(document.createElement('span'))
          .addClass(`filter ${dataKey}-filter`)
          .html(` ${lookup[dataKey].label}: `);

      filters.append(filterEl);

      // append text of selected filter as anchor elements
      filterEl.append(
        $(document.createElement('a')).addClass('focus-input')
          .attr('href', '#')
          .html(lookup[dataKey].html)
      );
    }
  });
}

function updatePriceHistogram(data) {
  const width = 720;
  const height = 300;
  const pad = [120, 15, 60, 60];
  const top = pad[0];
  const left = pad[3];
  const right = width - pad[1];
  const bottom = height - pad[2];
  const svg = d3.select('#price-histogram')
    .attr('viewBox', [0, 0, width, height].join(' '))
    .attr('preserveAspectRatio', 'xMinYMid meet');
  const formatDollars = (n) => `$${formatPrice(n)}`;
  let stdMinus;
  let stdPlus;

  const extent = [data.minimum, data.maximum];
  const bins = data.wage_histogram;
  const x = d3.scale.linear()
      .domain(extent)
      .range([left, right]);
  const countExtent = d3.extent(bins, (d) => d.count);
  const heightScale = d3.scale.linear()
      .domain([0].concat(countExtent))
      .range([0, 1, bottom - top]);

  d3.select('#avg-price-highlight')
    .text(formatDollars(data.average));

  let stdDevMin = data.average - data.first_standard_deviation;
  let stdDevMax = data.average + data.first_standard_deviation;

  if (isNaN(stdDevMin)) stdDevMin = 0;
  if (isNaN(stdDevMax)) stdDevMax = 0;

  d3.select('#standard-deviation-minus-highlight')
    .text(formatDollars(stdDevMin));

  d3.select('#standard-deviation-plus-highlight')
    .text(formatDollars(stdDevMax));

  let stdDev = svg.select('.stddev');
  if (stdDev.empty()) {
    stdDev = svg.append('g')
      .attr('transform', 'translate(0,0)')
      .attr('class', 'stddev');
    stdDev.append('rect')
      .attr('class', 'range-fill');
    stdDev.append('line')
      .attr('class', 'range-rule');
    const stdDevLabels = stdDev.append('g')
      .attr('class', 'range-labels')
      .selectAll('g.label')
      .data([
        { type: 'min', anchor: 'end', label: '-1 stddev' },
        { type: 'max', anchor: 'start', label: '+1 stddev' },
      ])
      .enter()
      .append('g')
        .attr('transform', 'translate(0,0)')
        .attr('class', (d) => `label ${d.type}`);
    stdDevLabels.append('line')
      .attr('class', 'label-rule')
      .attr({
        y1: -5,
        y2: 5,
      });
    const stdDevLabelsText = stdDevLabels.append('text')
      .attr('text-anchor', (d) => d.anchor)
      .attr('dx', (d, i) => 8 * (i ? 1 : -1));

    stdDevLabelsText.append('tspan')
      .attr('class', 'stddev-text');
    stdDevLabelsText.append('tspan')
      .attr('class', 'stddev-text-label');
  }

  stdMinus = data.average - data.first_standard_deviation;
  stdPlus = data.average + data.first_standard_deviation;

  if (isNaN(stdMinus)) {
    stdMinus = '$0';
  } else {
    stdMinus = formatDollars(stdMinus);
  }
  if (isNaN(stdPlus)) {
    stdPlus = '$0';
  } else {
    stdPlus = formatDollars(stdPlus);
  }


  d3.select('#standard-deviation-minus-highlight')
    .text(stdMinus);

  d3.select('#standard-deviation-plus-highlight')
    .text(stdPlus);


  let xAxis = svg.select('.axis.x');
  if (xAxis.empty()) {
    xAxis = svg.append('g')
      .attr('class', 'axis x');
  }

  let yAxis = svg.select('.axis.y');
  if (yAxis.empty()) {
    yAxis = svg.append('g')
      .attr('class', 'axis y');
  }

  let gBar = svg.select('g.bars');
  if (gBar.empty()) {
    gBar = svg.append('g')
      .attr('class', 'bars');
  }


  // draw proposed price line
  let pp = svg.select('g.pp');
  const ppOffset = -95;
  if (pp.empty()) {
    pp = svg.append('g')
      .attr('class', 'pp');

    pp.append('rect')
      .attr('y', ppOffset - 25)
      .attr('x', -55)
      .attr('class', 'pp-label-box')
      .attr('width', 110)
      .attr('height', 26)
      .attr('rx', 4)
      .attr('ry', 4);

    pp.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', ppOffset - 6)
      .attr('class', 'value proposed');

    pp.append('line');
  }

  // widen proposed price rect if more than 3 digits long
  if (data.proposedPrice.toString().replace('.', '').length > 3) {
    pp.select('rect').attr('width', 130);
    pp.select('text').attr('dx', 10);
  } else {
    pp.select('rect').attr('width', 110);
    pp.select('text').attr('dx', 0);
  }

  pp.select('line')
    .attr('y1', ppOffset)
    .attr('y2', (bottom - top) + 8);
  pp.select('.value')
    .text(`$${data.proposedPrice} proposed`);

  if (data.proposedPrice === 0) {
    pp.style('opacity', 0);
  } else {
    pp.style('opacity', 1);
  }

  // draw average line
  let avg = svg.select('g.avg');
  const avgOffset = -55;
  if (avg.empty()) {
    avg = svg.append('g')
      .attr('class', 'avg');

    avg.append('rect')
      .attr('y', avgOffset - 25)
      .attr('x', -55)
      .attr('class', 'avg-label-box')
      .attr('width', 110)
      .attr('height', 26)
      .attr('rx', 4)
      .attr('ry', 4);

    avg.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', avgOffset - 7)
      .attr('class', 'value average');

    avg.append('line');
  }

  avg.select('line')
    .attr('y1', avgOffset)
    .attr('y2', (bottom - top) + 8);
  avg.select('.value')
    .text(`${formatDollars(data.average)} average`);

  const bars = gBar.selectAll('.bar')
    .data(bins);

  bars.exit().remove();

  const enter = bars.enter().append('g')
    .attr('class', 'bar');
  enter.append('title');

  const step = (right - left) / bins.length;
  enter.append('rect')
    .attr('x', (d, i) => left + (i * step))
    .attr('y', bottom)
    .attr('width', step)
    .attr('height', 0);

  const title = templatize('{count} results from {min} to {max}');
  bars.select('title')
    .text((d, i) => {
      const inclusive = (i === bins.length - 1);
      const sign = inclusive ? '<=' : '<';
      return title({
        count: formatCommas(d.count),
        min: formatDollars(d.min),
        sign,
        max: formatDollars(d.max),
      });
    });

  const t = histogramUpdated
    ? svg.transition().duration(500)
    : svg;

  const stdDevWidth = x(stdDevMax) - x(stdDevMin);
  const stdDevTop = 85;
  stdDev = t.select('.stddev');
  stdDev
    .attr('transform', `translate(${[x(stdDevMin), stdDevTop]})`);

  stdDev.select('rect.range-fill')
    .attr('width', stdDevWidth)
    .attr('height', bottom - stdDevTop);

  stdDev.select('line.range-rule')
    .attr('x2', stdDevWidth);

  stdDev.select('.label.min .stddev-text')
    .text(formatDollars(stdDevMin))
    .attr({ x: 0, dy: 0 });

  stdDev.select('.label.min .stddev-text-label')
    .text('-1 std dev')
    .attr({ x: -8, dy: '15px' });

  stdDev.select('.label.max')
    .attr('transform', `translate(${[stdDevWidth, 0]})`);

  stdDev.select('.label.max .stddev-text-label')
    .text('+1 std dev')
    .attr({ x: 8, dy: '15px' });


  stdDev.select('.label.max .stddev-text')
    .text(formatDollars(stdDevMax));

  t.select('.avg')
    .attr('transform', `translate(${[~~x(data.average), top]})`);

  t.select('.pp')
    .attr('transform', `translate(${[~~x(data.proposedPrice), top]})`);

  t.selectAll('.bar')
    .each((d) => {
      d.x = x(d.min); // eslint-disable-line no-param-reassign
      d.width = x(d.max) - d.x; // eslint-disable-line no-param-reassign
      d.height = heightScale(d.count); // eslint-disable-line no-param-reassign
      d.y = bottom - d.height; // eslint-disable-line no-param-reassign
    })
    .select('rect')
      .attr('x', (d) => d.x)
      .attr('y', (d) => d.y)
      .attr('height', (d) => d.height)
      .attr('width', (d) => d.width);

  const ticks = bins.map((d) => d.min)
    .concat([data.maximum]);

  const xa = d3.svg.axis()
    .orient('bottom')
    .scale(x)
    .tickValues(ticks)
    .tickFormat((d, i) => {
      if (i === 0 || i === bins.length) {
        return formatDollars(d);
      }
      return formatPrice(d);
    });
  xAxis.call(xa)
    .attr('transform', `translate(${[0, bottom + 2]})`)
    .selectAll('.tick')
      .classed('primary', (d, i) => i === 0 || i === bins.length)
      .select('text')
        .classed('min', (d, i) => i === 0)
        .classed('max', (d, i) => i === bins.length)
        .style('text-anchor', 'end')
        .attr('transform', 'rotate(-35)');

  // remove existing labels
  svg.selectAll('text.label').remove();

  xAxis.append('text')
    .attr('class', 'label')
    .attr('transform', `translate(${[left + ((right - left) / 2), 45]})`)
    .attr('text-anchor', 'middle')
    .text('Ceiling price (hourly rate)');

  const yd = d3.extent(heightScale.domain());
  const ya = d3.svg.axis()
    .orient('left')
    .scale(d3.scale.linear()
      .domain(yd)
      .range([bottom, top]))
    .tickValues(yd);
  ya.tickFormat(formatCommas);
  yAxis.call(ya)
    .attr('transform', `translate(${[left - 2, 0]})`);

  yAxis.append('text')
    .attr('class', 'label')
    .attr('transform', `translate(${[-25, (height / 2) + 25]}) rotate(-90)`)
    .attr('text-anchor', 'middle')
    .text('# of results');

  histogramUpdated = true;
}

function update(submitFn, error, res) {
  search.classed('loading', false);
  request = null;

  if (error) {
    if (error === 'abort') {
      // ignore aborts
      return;
    }

    search.classed('error', true);

    loadingIndicator.select('.error-message')
      .text(error);
  } else {
    search.classed('error', false);
  }

  search.classed('loaded', true);

  updateDescription(res);
  updateCounter++;

  if ($('.proposed-price input').val()) {
    res.proposedPrice = $('.proposed-price input').val(); // eslint-disable-line no-param-reassign
    $('.proposed-price-highlight').html(`$${$('.proposed-price input').val()}`);
    $('.proposed-price-block').fadeIn();
  } else {
    res.proposedPrice = 0; // eslint-disable-line no-param-reassign
    $('.proposed-price-block').fadeOut();
  }

  if (res && res.results && res.results.length) {
    updatePriceHistogram(res);
    updateResults(form, res, submitFn);
  } else {
    res = EMPTY_DATA; // eslint-disable-line no-param-reassign
    // updatePriceRange(EMPTY_DATA);
    updatePriceHistogram(res);
    updateResults(form, res, submitFn);
  }
}

function submit(pushState) {
  let data = form.getData();

  data = arrayToCSV(data);

  inputs
    .filter(function filter() {
      return this.type !== 'radio' && this.type !== 'checkbox';
    })
    .classed('filter_active', function classed() {
      return !!this.value;
    });

  data.experience_range = `${$('#min_experience').val()},${$('#max_experience').val()}`;

  search.classed('loaded', false);
  search.classed('loading', true);

  // cancel the outbound request if there is one
  if (request) request.abort();
  const defaults = {
    histogram: HISTOGRAM_BINS,
  };
  request = api.get({
    uri: 'rates/',
    data: hourglass.extend(defaults, data),
  }, update.bind(this, submit));


  d3.select('#export-data')
    .attr('href', function updateQueryString() {
      return [
        this.href.split('?').shift(),
        hourglass.qs.format(data),
      ].join('?');
    });

  if (pushState) {
    const href = `?${hourglass.qs.format(data)}`;
    const didSearchChange = window.location.search !== href;

    history.pushState(null, null, href);

    if (didSearchChange) {
      ga('set', 'page', window.location.pathname +
                        window.location.search);
      ga('send', 'pageview');
    }
  }

  updateExcluded(form);
}

function popstate() {
  // read the query string and set values accordingly
  const data = hourglass.extend(
    form.getData(),
    hourglass.qs.parse(location.search)
  );
  inputs.on('change', null);
  form.setData(data);
  inputs.on('change', () => {
    submit(true);
  });

  const sort = parseSortOrder(data.sort);
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

  submit(false);
}

function initialize() {
  popstate();

  let autoCompReq;
  let searchTerms = '';

  $('#labor_category').autoComplete({
    minChars: 2,
    // delay: 5,
    delay: 0,
    cache: false,
    source(term, done) {
      // save inputted search terms for display later
      searchTerms = term;

      const lastTerm = hourglass.getLastCommaSeparatedTerm(term);

      if (autoCompReq) { autoCompReq.abort(); }
      const data = form.getData();
      autoCompReq = api.get({
        uri: 'search/',
        data: {
          q: lastTerm,
          query_type: data.query_type,
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
        selectedInput = `${$('#labor_category').val()}, `;
      }

      // update the search input field accordingly
      $('#labor_category').val(selectedInput);
    },
  });
}

function setupSortHeaders(headers) {
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

function setupColumnHeader(headers) {
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
    .call(setupSortHeaders);
}

function histogramToImg(e) {
  e.preventDefault();
  let svg = document.getElementById('price-histogram');
  const canvas = document.getElementById('graph');
  const serializer = new XMLSerializer();
  let img;
  let modalImg;

  svg = serializer.serializeToString(svg);

  // convert svg into canvas
  canvg(canvas, svg, { ignoreMouse: true, scaleWidth: 720, scaleHeight: 300 });

  if (typeof Blob !== 'undefined') {
    canvas.toBlob((blob) => {
      saveAs(blob, 'histogram.png');
    });
  } else {
    img = canvas.toDataURL('image/png');
    modalImg = new Image();
    modalImg.src = img;

    vex.open({
      content: 'Please right click the image and select "save as" to download the graph.',
      afterOpen(content) {
        return content.append(modalImg);
      },
      showCloseButton: true,
      contentCSS: {
        width: '800px',
      },
    });
  }
}

/*
  Dropdown with Multiple checkbox select with jQuery - May 27, 2013
  (c) 2013 @ElmahdiMahmoud
  license: http://www.opensource.org/licenses/mit-license.php
  // many edits by xtine
*/
$('.dropdown dt a').on('click', (e) => {
  $('.dropdown dd ul').slideToggle('fast');

  e.preventDefault();
});

$('.dropdown dd ul li a').on('click', (e) => {
  $('.dropdown dd ul').hide();

  e.preventDefault();
});

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

// initialize tooltipster.js
$('.tooltip').tooltipster({
  functionInit() {
    return $(this).attr('aria-label');
  },
});

sortHeaders.call(setupColumnHeader);

initialize();

$(document).bind('click', (e) => {
  const $clicked = $(e.target);
  if (!$clicked.parents().hasClass('dropdown')) $('.dropdown dd ul').hide();
});


$('.multiSelect input[type="checkbox"]').on('click', function onClick() {
  const title = $(this).next().html();

  if ($(this).is(':checked')) {
    const html = `<span title="${title}">${title}</span>`;

    $('.multiSel').append(html);
    $('.eduSelect').hide();
  } else {
    $(`span[title="${title}"]`).remove();
    $('.dropdown dt a').addClass('hide');
  }

  if (!$('.multiSelect input:checked').length) {
    $('.eduSelect').show();
  } else {
    $('.eduSelect').hide();
  }
});

if (getUrlParameterByName('education').length) {
  const parameters = getUrlParameterByName('education').split(',');

  $('.eduSelect').hide();

  parameters.forEach((param) => {
    const title = $(`.multiSelect input[type=checkbox][value=${param}]`)
      .attr('checked', true)
      .next()
      .html();

    $('.multiSel').append(`<span title="${title}">${title}</span>`);
  });
}

$('.slider').noUiSlider({
  start: [0, MAX_EXPERIENCE],
  step: 1,
  connect: true,
  range: {
    min: 0,
    max: MAX_EXPERIENCE,
  },
});

$('.slider').Link('lower').to($('#min_experience'), null, wNumb({ // eslint-disable-line new-cap
  decimals: 0,
}));
$('.slider').Link('upper').to($('#max_experience'), null, wNumb({ // eslint-disable-line new-cap
  decimals: 0,
}));

$('.slider').on({
  slide() {
    $('.noUi-horizontal .noUi-handle').addClass('filter_focus');
  },
  set() {
    $('.noUi-horizontal .noUi-handle').removeClass('filter_focus');

    submit(true);

    if ($('#min_experience').val() === '0' && $('#max_experience').val() === `${MAX_EXPERIENCE}`) {
      $('#min_experience, #max_experience').removeClass('filter_active');
    }
  },
});

// on load remove active class on experience slider
$('#min_experience, #max_experience').removeClass('filter_active');

// load experience range if query string exists
if (getUrlParameterByName('max_experience').length) {
  $('.slider').val([getUrlParameterByName('min_experience'),
    getUrlParameterByName('max_experience')]);
}

// restrict proposed price input to be numeric only
$('.proposed-price input').keypress((e) => {
  if (!isNumberOrPeriodKey(e)) {
    e.preventDefault();
  }
});

// trigger proposed button input
$('.proposed-price button').click(() => {
  if ($('.proposed-price input').val()) {
    $('.proposed-price-highlight').html(`$${$('.proposed-price input').val()}`);

    $('.proposed-price-block').fadeIn();
  } else {
    $('.proposed-price-block').fadeOut();
  }
});


if (getUrlParameterByName('proposed-price').length) {
  $('.proposed-price-highlight').html(`$${getUrlParameterByName('proposed-price')}`);
  $('.proposed-price-block').show();
}

$(document).keypress((e) => {
  // NOTE: JAS: Seems weird to apply this to the entire document
  if (e.which === 13) {
    $('.proposed-price button').trigger('click');
  }
});

$('.two-decimal-places').keyup(function onKeyUp() {
  // regex checks if there are more than 2 numbers after decimal point
  if (!(/^\d+(\.{0,1}\d{0,2})?$/.test(this.value))) {
    // cut off and prevent user from inputting more than 2 numbers after decimal place
    this.value = this.value.substring(0, this.value.length - 1);
  }
});

window.addEventListener('popstate', popstate);

histogramDownloadLink.addEventListener('click', histogramToImg, false);

form.on('submit', (data, e) => {
  e.preventDefault();
  submit(true);
});

/*
* For some reason, the browser's native form reset isn't working.
* So instead of just listening for a "reset" event and submitting,
* we hijack the click event on the reset button and reset the form
* manually.
*/
search.select('input[type="reset"]')
 .on('click', () => {
   form.reset();
   // NB: form.reset() doesn't reset hidden inputs,
   // so we need to do it ourselves.
   search.selectAll('input[type="hidden"]')
     .property('value', '');

   submit(true);
   d3.event.preventDefault();

   $('.multiSel').empty();
   $('.eduSelect').show();
   if ($('.multiSelect input:checked').length) {
     $('.multiSelect input:checked').attr('checked', false);
   }
   $('.slider').val([0, 45]);
 });

inputs.on('change', () => {
  submit(true);
});

d3.selectAll('a.merge-params')
  .on('click', () => {
    d3.event.preventDefault();
    form.set('exclude', '');
    submit(true);
  });
