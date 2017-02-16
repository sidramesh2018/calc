/* global window */
import xhr from 'xhr';
import qs from 'qs';

export default class API {
  constructor(basePath = '') {
    this.basePath = window.API_HOST || basePath;
    if (this.basePath.charAt(this.basePath.length - 1) !== '/') {
      this.basePath += '/';
    }
  }

  get({ uri, data }, callback) {
    let path = this.basePath + uri;
    if (data) {
      path += `?${qs.stringify(data)}`;
    }
    return xhr(path, {
      json: true,
    }, (err, res) => {
      if (err) {
        callback(err.toString());
      } else if (res.statusCode !== 200) {
        callback(res.rawRequest.statusText);
      } else {
        callback(null, res.body);
      }
    });
  }
}
