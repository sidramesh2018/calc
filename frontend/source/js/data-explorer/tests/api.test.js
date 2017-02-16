/* global window */

import xhr from 'xhr';
import MockXMLHttpRequest from 'mock-xmlhttprequest';

import API from '../api';

describe('API constructor', () => {
  it('defaults to relative path', () => {
    const api = new API();
    expect(api.basePath).toMatch('/');
  });

  it('allows setting of basePath in constructor', () => {
    const api = new API('/api');
    expect(api.basePath).toMatch('/api/');

    const api2 = new API('/api2/');
    expect(api2.basePath).toMatch('/api2/');
  });

  it('uses window.API_HOST if defined', () => {
    window.API_HOST = 'whatever';
    const api = new API();
    expect(api.basePath).toMatch('whatever/');
  });
});

describe('API get', () => {
  xhr.XMLHttpRequest = MockXMLHttpRequest;
  const api = new API();

  MockXMLHttpRequest.onSend = (mock) => {
    const responseHeaders = {
      'Content-Type': 'application/json',
    };

    if (mock.url === '/whatever') {
      mock.respond(200, responseHeaders, JSON.stringify({
        result: 'success',
      }));
    } else if (mock.url === '/data?param=value') {
      mock.respond(200, responseHeaders, JSON.stringify({
        result: 'data_success',
      }));
    } else if (mock.url === '/network_error') {
      mock.setNetworkError();
    } else {
      mock.respond(404, responseHeaders);
    }
  };

  it('works with just uri', (done) => {
    api.get({ uri: 'whatever' }, (err, res) => {
      expect(err).toBeFalsy();
      expect(res).toMatchObject({ result: 'success' });
      done();
    });
  });

  it('works with uri and data object', (done) => {
    api.get({ uri: 'data', data: { param: 'value' } }, (err, res) => {
      expect(err).toBeFalsy();
      expect(res).toMatchObject({ result: 'data_success' });
      done();
    });
  });

  it('callsback with string on non-200 response', (done) => {
    api.get({ uri: 'bad' }, (err, res) => {
      expect(res).toBeFalsy();
      expect(err).toMatch('Not Found');
      done();
    });
  });

  it('callsback with a string on network error', (done) => {
    api.get({ uri: 'network_error' }, (err, res) => {
      expect(res).toBeFalsy();
      expect(err).toMatch('Error: Internal XMLHttpRequest Error');
      done();
    });
  });
});
