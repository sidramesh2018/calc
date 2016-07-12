const gulp = require('gulp');
const sass = require('gulp-sass');
const cleancss = require('gulp-clean-css');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');

const dirs = {
  src: {
    style: 'hourglass_site/static_source/style/',
    scripts: 'hourglass_site/static_source/js/',
  },
  dest: {
    style: 'hourglass_site/static/hourglass_site/style/built/',
    scripts: {
      dataExplorer: 'hourglass_site/static/hourglass_site/js/built/data-explorer',
      common: 'hourglass_site/static/hourglass_site/js/built/common',
    },
  },
};

const paths = {
  sass: '**/*.scss',
  js: '**/*.js',
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

// default task
// running `gulp` will default to watching and dist'ing files
gulp.task('default', ['watch']);

// production build task
// will need to run before collectstatic
// `npm run gulp -- build` or `gulp run build` if gulp-cli is installed globally
gulp.task('build', ['sass', 'js']);

// watch files for changes
gulp.task('watch', ['sass', 'js'], () => {
  gulp.watch(dirs.src.style + paths.sass, ['sass']);
  gulp.watch(dirs.src.scripts + paths.js, ['js']);
});

// compile SASS sources
gulp.task('sass', () => gulp.src(dirs.src.style + paths.sass)
  .pipe(sass())
  .pipe(gulp.dest(dirs.dest.style))
  .pipe(rename({ suffix: '.min' }))
  .pipe(sourcemaps.init())
    .pipe(cleancss())
  .pipe(sourcemaps.write('./'))
  .pipe(gulp.dest(dirs.dest.style))
);

gulp.task('js', ['js:legacy']);

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
    paths.dataExplorer.index.map((p) => dirs.src.scripts + p),
    dirs.dest.scripts.dataExplorer
  )
);

gulp.task('js:common:base', () => concatAndMapSources(
    'base.min.js',
    paths.common.base.map((p) => dirs.src.scripts + p),
    dirs.dest.scripts.common
  )
);

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
