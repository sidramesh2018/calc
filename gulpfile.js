var gulp = require('gulp');
var sass = require('gulp-sass');
var watch = require('gulp-watch');
var cleancss = require('gulp-clean-css');
var concat = require('gulp-concat');
var sourcemaps = require('gulp-sourcemaps');
var rename = require('gulp-rename');
var gutil = require('gulp-util');

var dirs = {
  src: {
    style: 'hourglass_site/static_source/style/',
    scripts: 'hourglass_site/static_source/js/',
  },
  dest: {
    style: 'hourglass_site/static/hourglass_site/style/built/',
    scripts: 'hourglass_site/static/hourglass_site/js/built/',
  }
};

var paths = {
  sass: '**/*.scss',
  js: '**/*.js',
  jsLegacy: {
    index: [
      'vendor/rgbcolor.js',
      'vendor/StackBlur.js',
      'vendor/canvg.js',
      'vendor/canvas-toBlob.js',
      'vendor/FileSaver.js',
      'vendor/jquery.auto-complete.min.js',
      'index.js'
    ],
    base: [
      'vendor/d3.v3.min.js',
      'vendor/jquery.min.js',
      'vendor/query.xdomainrequest.min.js',
      'vendor/formdb.min.js',
      'hourglass.js',
      'vendor/jquery.tooltipster.js',
      'vendor/jquery.nouislider.all.min.js',
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
gulp.task('watch', ['sass', 'js'], function () {
    gulp.watch(dirs.src.style + paths.sass, ['sass']);
    gulp.watch(dirs.src.scripts + paths.js, ['js']);
});

// compile SASS sources
gulp.task('sass', function () {
    return gulp.src(dirs.src.style + paths.sass)
      .pipe(sass())
      .pipe(gulp.dest(dirs.dest.style))
      .pipe(rename({suffix: '.min'}))
      .pipe(sourcemaps.init())
        .pipe(cleancss())
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(dirs.dest.style));
});

gulp.task('js', ['js:legacy']);

gulp.task('js:legacy', ['js:legacy:index', 'js:legacy:base']);

function concatAndMapSources(name, paths, dest) {
  return gulp.src(paths)
    .pipe(sourcemaps.init())
      .pipe(concat(name))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
}

gulp.task('js:legacy:index', function () {
  return concatAndMapSources(
    'index.min.js',
    paths.jsLegacy.index.map(function (p) { return dirs.src.scripts + p; }),
    dirs.dest.scripts
  );
});

gulp.task('js:legacy:base', function () {
  return concatAndMapSources(
    'base.min.js',
    paths.jsLegacy.base.map(function (p) { return dirs.src.scripts + p; }),
    dirs.dest.scripts
  );
});

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', function() {
  process.exit(1);
});
