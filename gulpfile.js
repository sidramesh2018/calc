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
const gulpif = require('gulp-if');
const gutil = require('gulp-util');
const uglify = require('gulp-uglify');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const browserify = require('browserify');
const watchify = require('watchify');
const envify = require('envify/custom');
const babelify = require('babelify');
const del = require('del');
const webpackStream = require('webpack-stream');
const webpack = require('webpack');

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
    noBrowserify: true,
    vendor: [
      'vendor/d3.v3.min.js',
      'vendor/jquery.min.js',
      'vendor/query.xdomainrequest.min.js',
      'vendor/jquery.tooltipster.js',
      'vendor/jquery.nouislider.all.min.js',
    ],
  },
  // Data Explorer scripts
  dataExplorer: {
    noBrowserify: true,
    dirName: 'data-explorer',
    vendor: [
      'vendor/rgbcolor.js',
      'vendor/StackBlur.js',
      'vendor/canvg.js',
      'vendor/canvas-toBlob.js',
      'vendor/FileSaver.js',
      'vendor/jquery.auto-complete.min.js',
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

const browserifiedBundles = [];
const vendoredBundles = [];

Object.keys(bundles).forEach((name) => {
  const options = bundles[name];
  const dirName = options.dirName || name;
  const noBrowserify = options.noBrowserify;
  const vendor = options.vendor || [];
  const entryName = `${name}Entry`;
  const outfileName = `${name}Outfile`;

  dirs.dest.scripts[name] = `${BUILT_FRONTEND_DIR}/js/${dirName}`;

  if (!noBrowserify) {
    const browserifiedBundleName = `js:${dirName}`;
    paths[entryName] = `${dirName}/index.js`;
    paths[outfileName] = 'index.min.js';

    gulp.task(browserifiedBundleName, () =>
      browserifyBundle( // eslint-disable-line no-use-before-define
        path.join(dirs.src.scripts, paths[entryName]),
        dirs.dest.scripts[name],
        paths[outfileName]));

    browserifiedBundles.push(browserifiedBundleName);
  }

  if (vendor.length) {
    const vendoredBundleName = `js:${dirName}:vendor`;
    gulp.task(vendoredBundleName, () =>
      concatAndMapSources(  // eslint-disable-line no-use-before-define
        'vendor.min.js',
        vendor.map(p => dirs.src.scripts + p),
        dirs.dest.scripts[name]));

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

  // Note: browserified and webpack'd bundles set up their own watch handling
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
gulp.task('js', ['lint', 'js:vendor', 'js:data-explorer'].concat(browserifiedBundles));

gulp.task('js:vendor', vendoredBundles);

function concatAndMapSources(name, sources, dest) {
  return gulp.src(sources)
    .pipe(sourcemaps.init())
      .pipe(concat(name))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
}

// boolean flag to indicate to watchify/browserify that it should set up
// its rebundling
let isWatching = false;
gulp.task('set-watching', () => {
  isWatching = true;
});

function browserifyBundle(entryPath, outputPath, outputFile) {
  // ref: https://gist.github.com/danharper/3ca2273125f500429945
  let bundler = browserify(entryPath, {
    debug: true,
    cache: {},
    packageCache: {},
  });

  // Some modules are referenced in the source code for
  // Enzyme, but they're never actually loaded because they're only
  // needed for older versions of React, so we'll explicitly tell
  // Browserify to ignore them here.
  bundler = bundler
    .exclude('react/addons')
    .exclude('react/lib/ReactContext')
    .exclude('react/lib/ExecutionEnvironment');

  bundler = bundler
    .transform(envify({ NODE_ENV: process.env.NODE_ENV }), { global: true })
    .transform(babelify.configure({ presets: ['es2015'] }));

  if (process.env.NODE_ENV === 'production') {
    // Here we use uglifyify--not to be confused with uglify--to uglify
    // each individual module by itself, which allows us to excise
    // unused dependencies based on our build configuration. We are
    // also passing arguments to bundler.transform() in a weird order,
    // but it's what uglifyify's docs recommend and it seems to work,
    // so whatever.
    bundler = bundler.transform({
      global: true,
    }, 'uglifyify');
  }

  if (isWatching) {
    bundler = watchify(bundler);
  }

  function rebundle() {
    bundler.bundle()
      .on('error', (err) => {
        gutil.beep();
        gutil.log(gutil.colors.red(`Error (browserify):\n${err.toString()}`));
        if (!isWatching) {
          throw err;
        }
      })
      .pipe(source(outputFile))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(gulpif(isProd, uglify()))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(outputPath))
      .on('data', (file) => {
        const pathname = path.relative(__dirname, file.path);

        gutil.log(`Wrote ${pathname}.`);
      });
  }

  if (isWatching) {
    bundler.on('update', () => {
      gutil.log(`-> Rebundling ${entryPath}`);
      rebundle();
    });
  }

  rebundle();
  return bundler;
}

gulp.task('js:data-explorer', () => {
  const dirName = bundles.dataExplorer.dirName;
  const entry = path.join(dirs.src.scripts, dirName, 'index.js');
  const plugins = [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': isProd ? '"production"' : '""'
    }),
  ];

  if (isProd) {
    plugins.push(new webpack.optimize.UglifyJsPlugin());
  }

  // Note: we do not want to return this stream back to gulp
  gulp.src(entry)
    .pipe(webpackStream({
      watch: isWatching,
      resolve: {
        extensions: ['.js', '.jsx'],
      },
      devtool: 'source-map',
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
      output: {
        filename: 'index.min.js',
      },
    }, webpack))
    .pipe(gulp.dest(`${BUILT_FRONTEND_DIR}/js/${dirName}`));
});

gulp.task('lint', () => gulp.src(path.join(dirs.src.scripts, paths.js))
    .pipe(eslint())
    .pipe(eslint.format()));

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
