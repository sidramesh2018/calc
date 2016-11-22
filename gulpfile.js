'use strict'; // eslint-disable-line

require('dotenv').config({ silent: true });

if (!('DEBUG' in process.env)) {
  process.env.NODE_ENV = 'production';
}

const path = require('path');

const gulp = require('gulp');
const sass = require('gulp-sass');
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
const babelify = require('babelify');
const del = require('del');

const BUILT_FRONTEND_DIR = 'frontend/static/frontend/built';

const dirs = {
  src: {
    style: 'frontend/source/sass/',
    scripts: 'frontend/source/js/',
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
  js: '**/*.js',
};

const bundles = {
  // Scripts (vendor libs) common to CALC 1 and 2
  common: {
    noBrowserify: true,
    vendor: [
      'vendor/d3.v3.min.js',
      'vendor/jquery.min.js',
      'vendor/query.xdomainrequest.min.js',
      'vendor/formdb.min.js',
      'vendor/jquery.tooltipster.js',
      'vendor/jquery.nouislider.all.min.js',
    ],
  },
  // CALC 1.0 scripts
  dataExplorer: {
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
  // CALC 2.0 Data Capture scripts
  dataCapture: {
    dirName: 'data-capture',
  },
  // Styleguide scripts
  styleguide: {},
  // CALC 2.0 Tests
  tests: {},
};

const browserifiedBundles = [];
const vendoredBundles = [];

Object.keys(bundles).forEach(name => {
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
      browserifyBundle(  // eslint-disable-line
        path.join(dirs.src.scripts, paths[entryName]),
        dirs.dest.scripts[name],
        paths[outfileName]
      )
    );
    browserifiedBundles.push(browserifiedBundleName);
  }

  if (vendor.length) {
    const vendoredBundleName = `js:${dirName}:vendor`;
    gulp.task(vendoredBundleName, () => concatAndMapSources(  // eslint-disable-line
      'vendor.min.js',
      vendor.map((p) => dirs.src.scripts + p),
      dirs.dest.scripts[name]
    ));
    vendoredBundles.push(vendoredBundleName);
  }
});

const isInDocker = ('DDM_IS_RUNNING_IN_DOCKER' in process.env);

// default task
// running `gulp` will default to watching and dist'ing files
gulp.task('default', ['watch']);

// production build task
// will need to run before collectstatic
// `npm run gulp -- build` or `gulp run build` if gulp-cli is installed globally
gulp.task('build', ['sass', 'js']);

// watch files for changes
gulp.task('watch', ['set-watching', 'sass', 'js'], () => {
  gulp.watch(path.join(dirs.src.style, paths.sass), ['sass']);

  // browserified bundles set up their own watch handling (via watchify)
  // so we don't want to re-trigger them here, ref #437
  gulp.watch(path.join(dirs.src.scripts, paths.js), ['lint', 'js:legacy']);
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
  .pipe(sourcemaps.init())
    .pipe(sass().on('error', sass.logError))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cleancss())
  .pipe(sourcemaps.write('./'))
  .pipe(gulp.dest(dirs.dest.style.built))
);

// Compile and lint JavaScript sources
gulp.task('js', ['lint'].concat(browserifiedBundles).concat(['js:legacy']));

gulp.task('js:legacy', vendoredBundles);

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
  return;
});

function browserifyBundle(entryPath, outputPath, outputFile) {
  // ref: https://gist.github.com/danharper/3ca2273125f500429945
  let bundler = browserify(entryPath, {
    debug: true,
    cache: {},
    packageCache: {},
  })
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
        .pipe(gulpif(process.env.NODE_ENV === 'production', uglify()))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(outputPath))
      .on('data', file => {
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

gulp.task('lint', () => {
  const opts = {};
  if (isInDocker) {
    opts.rules = {
      // Until https://github.com/benmosher/eslint-plugin-import/issues/142
      // is fixed, we need to disable the following rule for Docker support.
      'import/no-unresolved': 0,
    };
  }

  return gulp.src(path.join(dirs.src.scripts, paths.js))
    .pipe(eslint(opts))
    .pipe(eslint.format());
});

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
