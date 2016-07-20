'use strict'; // eslint-disable-line

const path = require('path');

const gulp = require('gulp');
const sass = require('gulp-sass');
const cleancss = require('gulp-clean-css');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');
const eslint = require('gulp-eslint');
const gutil = require('gulp-util');
const uglify = require('gulp-uglify');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const browserify = require('browserify');
const watchify = require('watchify');
const babelify = require('babelify');
const del = require('del');

const dirs = {
  src: {
    style: 'hourglass_site/static_source/style/',
    scripts: 'hourglass_site/static_source/js/',
  },
  dest: {
    style: {
      built: 'hourglass_site/static/hourglass_site/style/built',
    },
    scripts: {
      // Scripts (vendor libs) common to CALC 1 and 2
      common: 'hourglass_site/static/hourglass_site/js/built/common',
      // CALC 1.0 scripts
      dataExplorer: 'hourglass_site/static/hourglass_site/js/built/data-explorer',
      // CALC 2.0/ Data Capture scripts
      dataCapture: 'hourglass_site/static/hourglass_site/js/built/data-capture',
    },
  },
};

const paths = {
  sass: '**/*.scss',
  js: '**/*.js',
  dataCaptureEntry: 'data-capture/index.js',
  dataCaptureOutfile: 'index.min.js',
};

const bundles = {
  common: {
    base: [
      'vendor/d3.v3.min.js',
      'vendor/jquery.min.js',
      'vendor/query.xdomainrequest.min.js',
      'vendor/formdb.min.js',
      'common/hourglass.js',
      'vendor/jquery.tooltipster.js',
      'vendor/jquery.nouislider.all.min.js',
    ],
  },
  dataExplorer: {
    index: [
      'vendor/rgbcolor.js',
      'vendor/StackBlur.js',
      'vendor/canvg.js',
      'vendor/canvas-toBlob.js',
      'vendor/FileSaver.js',
      'vendor/jquery.auto-complete.min.js',
      'data-explorer/index.js',
    ],
  },
};

let isWatching = false;

// default task
// running `gulp` will default to watching and dist'ing files
gulp.task('default', ['watch']);

// production build task
// will need to run before collectstatic
// `npm run gulp -- build` or `gulp run build` if gulp-cli is installed globally
gulp.task('build', ['sass', 'js']);

// watch files for changes
gulp.task('watch', ['sass', 'js'], () => {
  isWatching = true;
  gulp.watch(path.join(dirs.src.style, paths.sass), ['sass']);
  gulp.watch(path.join(dirs.src.scripts, paths.js), ['js']);
});

gulp.task('clean', () => {
  function getPaths(obj) {
    return Object.keys(obj).map((k) => path.join(obj[k], '**/*'));
  }

  const styleDirs = getPaths(dirs.dest.style);
  const scriptDirs = getPaths(dirs.dest.scripts);

  del([].concat(styleDirs, scriptDirs));
});

// compile SASS sources
gulp.task('sass', () => gulp.src(path.join(dirs.src.style, paths.sass))
  .pipe(sass())
  .pipe(rename({ suffix: '.min' }))
  .pipe(sourcemaps.init())
    .pipe(cleancss())
  .pipe(sourcemaps.write('./'))
  .pipe(gulp.dest(dirs.dest.style.built))
);

// Compile and lint JavaScript sources
gulp.task('js', ['lint', 'js:data-capture', 'js:legacy']);

gulp.task('js:legacy', ['js:data-explorer:index', 'js:common:base']);

function concatAndMapSources(name, sources, dest) {
  return gulp.src(sources)
    .pipe(sourcemaps.init())
      .pipe(concat(name))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
}

gulp.task('js:data-explorer:index', () => concatAndMapSources(
    'index.min.js',
    bundles.dataExplorer.index.map((p) => dirs.src.scripts + p),
    dirs.dest.scripts.dataExplorer
  )
);

gulp.task('js:common:base', () => concatAndMapSources(
    'base.min.js',
    bundles.common.base.map((p) => dirs.src.scripts + p),
    dirs.dest.scripts.common
  )
);


function browserifyBundle(entryPath, outputPath, outputFile) {
  // ref: https://gist.github.com/danharper/3ca2273125f500429945
  let bundler = browserify(entryPath, { debug: true })
    .transform(babelify.configure({ presets: ['es2015'] }));

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
        .pipe(uglify())
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(outputPath));
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

gulp.task('js:data-capture', () =>
  browserifyBundle(
    path.join(dirs.src.scripts, paths.dataCaptureEntry),
    dirs.dest.scripts.dataCapture,
    paths.dataCaptureOutfile
  )
);

gulp.task('lint', () => gulp.src(path.join(dirs.src.scripts, paths.js))
  .pipe(eslint())
  .pipe(eslint.format())
);

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
