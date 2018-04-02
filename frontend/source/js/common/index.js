
// entrypoint for common bundle
// this is where modules should be `require(...)`'d

require('babel-polyfill');
require('raf/polyfill');

global.$ = require('jquery');

global.jQuery = global.$;

require('../vendor/jquery.tooltipster');

require('./dap-hacks');
require('./usermenu');
