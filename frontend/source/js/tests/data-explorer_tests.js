/* global QUnit document $ */
import {
  parseQuery,
  joinQuery,
} from '../data-explorer/util';

QUnit.module('data-explorer');

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
