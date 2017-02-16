const hourglass = {};

/* eslint-disable */
(function(hourglass) {

  // enable CORS support
  $.support.cors = true;

  /**
   * The API class is used to access the Hourglass REST API. Usage:
   *
   * var api = hourglass.API();
   * api.get("uri", function(error, data) {
   *   if (error) return console.log("error:", error.statusText);
   * });
   *
   * // e.g. for paginated responses
   * api.get({
   *   uri: "rates",
   *   data: {page: 2, ...}
   * }, function(error, data) {
   * });
   */
  hourglass.API = function(path) {
    if (!(this instanceof hourglass.API)) {
      return new hourglass.API(path);
    }
    this.path = path || window.API_HOST;
    if (this.path.charAt(this.path.length - 1) !== '/') {
      this.path += '/';
    }
  };

  hourglass.API.prototype = {
    /**
     * get the fully qualified URL for a given request, specified either as a
     * URI string or a "request" object with either a .url or .uri property.
     */
    url: function(request) {
      var uri = (typeof request === "object")
        ? request.uri || request.url
        : request;
      // strip the preceding slash
      if (uri.charAt(0) === '/') uri = uri.substr(1);
      // TODO: merge request.data if provided and uri includes "?"
      return (this.path + uri);
    },

    /**
     * perform an API request, where `request` is a URI (string)
     * or an object with a `uri` property and an optional `data`
     * object containing query string parameters. The `callback`
     * function is called node-style ("error-first"):
     *
     * api.get("blarg", function(error, data) {
     *   if (error) return console.error("error:", error);
     * });
     *
     * api.get("rates/", function(error, data) {
     *   // do something with data
     * });
     */
    get: function(request, callback) {  // TODO JAS: move into rates-request
      var url = this.url(request);
      return $.ajax({
          url: url,
          dataType: 'json',
          data: request.data
        })
        .done(function(data) {
          return callback(null, data);
        })
        .fail(function(req, status, error) {
          return callback(error);
        });
    }
  };

  hourglass.getLastCommaSeparatedTerm = function getLastCST(term) {
    var pieces = term.split(/\s*,\s*/);

    return pieces[pieces.length-1];
  };
})(hourglass);
/* eslint-enable */

module.exports = hourglass;
