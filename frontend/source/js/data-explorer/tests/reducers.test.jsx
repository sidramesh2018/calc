import * as reducers from '../reducers';

import { MAX_QUERY_LENGTH } from '../constants';

describe('reducers.q()', () => {
  it('truncates to MAX_QUERY_LENGTH', () => {
    const query = Array(MAX_QUERY_LENGTH + 5).join('x');
    expect(reducers.q(query, { type: 'WHATEVER' }).length).toBe(MAX_QUERY_LENGTH);
  });
});
