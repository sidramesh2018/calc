'use strict'; // eslint-disable-line

require('dotenv').config({ silent: true });

if (!('DEBUG' in process.env)) {
  process.env.NODE_ENV = 'production';
}

const spawn = require('child_process').spawn;
const path = require('path');

const gulp = require('gulp');
const sass = require('gulp-sass');
const eyeglass = require('eyeglass');
const cleancss = require('gulp-clean-css');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');
const eslint = require('gulp-eslint');
const gutil = require('gulp-util');
const del = require('del');
const webpackStream = require('webpack-stream');
const webpack = require('webpack');
const named = require('vinyl-named');
const plumber = require('gulp-plumber');

const BUILT_FRONTEND_DIR = 'frontend/static/frontend/built';

const isProd = process.env.NODE_ENV === 'production';
gutil.log(`Gulp is running in ${isProd ? 'production' : 'development'} mode`);

const dirs = {
  src: {
    style: 'frontend/source/sass/',
    scripts: 'frontend/source/js/',
    sphinx: 'docs/',
  },
  dest: {
    style: {
      built: `${BUILT_FRONTEND_DIR}/style`,
    },
    scripts: {},
  },
};

const paths = {
  sass: '**/*.scss',
  js: '**/*.@(js|jsx)',
  sphinx: '*.@(md|py|rst)',
};

const bundles = {
  // Scripts (vendor libs) common to CALC 1 and 2
  common: {
    vendor: [
      'vendor/d3.v3.min.js',
      'vendor/jquery.1.11.1.js',
      'vendor/jquery.xdomainrequest.js',
      'vendor/jquery.tooltipster.js',
      'vendor/jquery.nouislider.all.min.js',
    ],
  },
  // Data Explorer scripts
  dataExplorer: {
    dirName: 'data-explorer',
    vendor: [
      'vendor/rgbcolor.js',
      'vendor/StackBlur.js',
      'vendor/canvg.js',
      'vendor/canvas-toBlob.js',
      'vendor/FileSaver.js',
      'vendor/jquery.auto-complete.js',
    ],
  },
  // Data Capture scripts
  dataCapture: {
    dirName: 'data-capture',
  },
  // Styleguide scripts
  styleguide: {},
  // Test scripts
  tests: {},
  // Common scripts
  shared: {
    dirName: 'common',
  },
};

const vendoredBundles = [];

// Generate tasks for all the vendor bundles
Object.keys(bundles).forEach((name) => {
  const options = bundles[name];
  const dirName = options.dirName || name;
  const vendor = options.vendor || [];

  if (vendor.length) {
    const vendoredBundleName = `js:${dirName}:vendor`;
    gulp.task(vendoredBundleName, () =>
      concatAndMapSources(  // eslint-disable-line no-use-before-define
        `${dirName}.vendor.js`,
        vendor.map(p => dirs.src.scripts + p),
        `${BUILT_FRONTEND_DIR}/js/`));

    vendoredBundles.push(vendoredBundleName);
  }
});


// default task
// running `gulp` will default to watching and dist'ing files
gulp.task('default', ['watch']);

gulp.task('sphinx', (cb) => {
  const sphinx = spawn('make', ['html'], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '/docs'),
    shell: true,
  });
  sphinx.on('exit', (code) => {
    if (code !== 0) {
      cb(new Error('Sphinx failed!'));
      return;
    }
    cb(null);
  });
});

// production build task
// will need to run before collectstatic
// `npm run gulp -- build` or `gulp run build` if gulp-cli is installed globally
gulp.task('build', ['sass', 'js', 'sphinx']);

// watch files for changes
gulp.task('watch', ['set-watching', 'sass', 'js', 'sphinx'], () => {
  gulp.watch(path.join(dirs.src.sphinx, paths.sphinx), ['sphinx']);
  gulp.watch(path.join(dirs.src.style, paths.sass), ['sass']);
  gulp.watch(path.join(dirs.src.scripts, paths.js), ['lint']);

  // Note: wepback bundles set up their own watch handling
  // so we don't want to re-trigger them here, ref #437
  gulp.watch(path.join(dirs.src.scripts, 'vendor', paths.js), ['js:vendor']);
});

gulp.task('clean', () => {
  function getPaths(obj) {
    return Object.keys(obj).map(k => path.join(obj[k], '**/*'));
  }

  const styleDirs = getPaths(dirs.dest.style);
  const scriptDirs = getPaths(dirs.dest.scripts);

  del([].concat(styleDirs, scriptDirs));
});

// compile SASS sources
gulp.task('sass', () => gulp.src(path.join(dirs.src.style, paths.sass))
  .pipe(sourcemaps.init())
    .pipe(sass(eyeglass()).on('error', sass.logError))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cleancss())
  .pipe(sourcemaps.write('./'))
  .pipe(gulp.dest(dirs.dest.style.built)));

// Compile and lint JavaScript sources
gulp.task('js', ['lint', 'js:vendor', 'js:webpack']);

gulp.task('js:vendor', vendoredBundles);

function concatAndMapSources(name, sources, dest) {
  return gulp.src(sources)
    .pipe(sourcemaps.init())
      .pipe(concat(name))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
}

// boolean flag to indicate to webpack that it should set up its watching
let isWatching = false;
gulp.task('set-watching', () => {
  isWatching = true;
});

gulp.task('js:webpack', () => {
  const sources = Object.keys(bundles).map((name) => {
    const options = bundles[name];
    const dirName = options.dirName || name;
    return path.join(dirs.src.scripts, dirName, 'index.js');
  });

  const plugins = [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': isProd ? '"production"' : '""',
    }),
  ];

  if (isProd) {
    plugins.push(new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
    }));
  }

  return gulp.src(sources)
    .pipe(plumber())
    .pipe(named((file) => {
      // All of our bundle entry files are of the form  "/some/path/index.js".
      // We'll use the last folder name to generate the file name of the
      // bundles (ie, "path.js") so that they're not all called "index.js".
      const parts = file.path.split(path.sep);
      const lastFolderName = parts[parts.length - 2];
      return lastFolderName;
    }))
    .pipe(webpackStream({
      watch: isWatching,
      resolve: {
        extensions: ['.js', '.jsx'],
      },
      stats: {},
      devtool: isProd ? 'source-map' : 'eval-source-map',
      module: {
        rules: [
          {
            test: /\.jsx?$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            options: {
              presets: ['es2015', 'react'],
              cacheDirectory: true,
            },
          },
        ],
      },
      plugins,
    }, webpack))
    .pipe(gulp.dest(`${BUILT_FRONTEND_DIR}/js/`));
});

gulp.task('lint', () => gulp.src(path.join(dirs.src.scripts, paths.js))
    .pipe(eslint())
    .pipe(eslint.format()));

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
