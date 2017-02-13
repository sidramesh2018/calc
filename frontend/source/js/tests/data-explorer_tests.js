/* global QUnit document $ */
import { appendHighlightedTerm } from '../data-explorer/autocomplete';
import {
  parseQuery,
  joinQuery,
} from '../data-explorer/util';

QUnit.module('data-explorer');

QUnit.test('appendHighlightedTerm() prevents stored XSS', (assert) => {
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'Project Manager of <script>alert("DOOM")</script>',
      'proj manager',
    ).html(),
    '<b>Proj</b>ect <b>Manager</b> of &lt;script&gt;alert("DOOM")&lt;/script&gt;',
  );
});

QUnit.test('appendHighlightedTerm() works', (assert) => {
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      'super').html(),
    '<b>super</b>duperman');

  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      'uper').html(),
    's<b>uper</b>d<b>uper</b>man');

  // test to make sure it doesn't blow up on special-character-only search term
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      '{{{').html(),
    'superduperman');
});

QUnit.test('parseQuery() works', (assert) => {
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

QUnit.test('joinQuery() works', (assert) => {
  assert.equal(joinQuery({ foo: 'bar', baz: 'quux hi' }),
               '?foo=bar&baz=quux%20hi');
});
