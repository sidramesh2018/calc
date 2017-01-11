import * as util from '../util';

describe('util.formatFriendlyPrice()', () => {
  it('should return price w/o cents if price is integral', () => {
    expect(util.formatFriendlyPrice(1)).toBe('1');
  });

  it('should return price w/ cents if price is float', () => {
    expect(util.formatFriendlyPrice(1.1)).toBe('1.10');
  });
});
