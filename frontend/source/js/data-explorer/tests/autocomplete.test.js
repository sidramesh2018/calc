import { processResults } from '../autocomplete';

describe('autocomplete.processResults', () => {
  const makeResults = () => [
    { labor_category: 'barista', count: 5, unused: 'blah' },
    { labor_category: 'chimney sweep', count: 2, unused: 'bloop' },
  ];

  it('should return [] on error', () => {
    const r = processResults('an error', makeResults());
    expect(r).toBeInstanceOf(Array);
    expect(r.length).toBe(0);
  });

  it('should return [] if result undefined', () => {
    const r = processResults(null, undefined);
    expect(r).toBeInstanceOf(Array);
    expect(r.length).toBe(0);
  });

  it('should return [] if result is empty', () => {
    const r = processResults(null, []);
    expect(r).toBeInstanceOf(Array);
    expect(r.length).toBe(0);
  });

  it('should return formatted categories', () => {
    const r = processResults(null, makeResults());
    expect(r).toEqual(expect.arrayContaining([
      { term: 'barista', count: 5 },
      { term: 'chimney sweep', count: 2 },
    ]));
    expect(r.length).toBe(2);
  });

  it('should default to 20 max categories', () => {
    const lotsOfResults = [];
    for (let i = 0; i < 30; i++) {
      lotsOfResults.push({ labor_category: `${i}`, count: i });
    }
    const r = processResults(null, lotsOfResults);
    expect(r.length).toBe(20);
  });
});
