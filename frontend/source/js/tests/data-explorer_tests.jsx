/* global QUnit document $ */

import React from 'react';
import { render } from 'enzyme';

import { Highlights } from '../data-explorer/components/highlights';
import { appendHighlightedTerm } from '../data-explorer/autocomplete';
import {
  parseQuery,
  joinQuery,
} from '../data-explorer/util';

QUnit.module('data-explorer');

QUnit.test('<Highlights> should render prices', assert => {
  const wrapper = render(
    <Highlights stdDeviation={1.1} avgPrice={2.1} proposedPrice={5} />
  );
  assert.equal(wrapper.find('.sd-highlight').first().text(), '$1',
               'Standard deviation -1 is rendered');
  assert.equal(wrapper.find('.avg-price-highlight').text(), '$2',
               'Average price is rendered');
  assert.equal(wrapper.find('.sd-highlight').last().text(), '$3',
               'Standard deviation +1 is rendered');
  assert.equal(wrapper.find('.proposed-price-highlight').text(), '$5',
               'Proposed price is rendered');
});

QUnit.test('appendHighlightedTerm() prevents stored XSS', assert => {
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'Project Manager of <script>alert("DOOM")</script>',
      'proj manager'
    ).html(),
    '<b>Proj</b>ect <b>Manager</b> of &lt;script&gt;alert("DOOM")&lt;/script&gt;'
  );
});

QUnit.test('parseQuery() works', assert => {
  assert.deepEqual(
    parseQuery('?foo=bar'),
    { foo: 'bar' },
    'parses a single value with ? prefix');
  assert.deepEqual(
    parseQuery('?foo=bar&baz=qux'),
    { foo: 'bar', baz: 'qux' },
    'parses two values');
  assert.deepEqual(
    parseQuery('?foo=foo+bar'),
    { foo: 'foo bar' },
    'parses "+" as space');
  assert.deepEqual(
    parseQuery('?foo=foo%20bar'),
    { foo: 'foo bar' },
    'parses "%20" as spaces');
});

QUnit.test('joinQuery() works', assert => {
  assert.equal(joinQuery({ foo: 'bar', baz: 'quux hi' }),
               '?foo=bar&baz=quux%20hi');
});
