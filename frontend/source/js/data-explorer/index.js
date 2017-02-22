
// entrypoint for data-explorer
// this is where modules should be `require(...)`'d

require('babel-polyfill/dist/polyfill');

require('../common/dap-hacks');
require('../common/usermenu');
require('./explorer');
