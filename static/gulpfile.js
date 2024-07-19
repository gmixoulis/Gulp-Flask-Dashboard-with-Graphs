import gulp from "gulp";
import path from 'path';
import gulpSass from "gulp-sass";
import concat from "gulp-concat";
import imagemin from "gulp-imagemin";
import sourcemaps from "gulp-sourcemaps";
import autoprefixer from "gulp-autoprefixer";
import sassCompiler from "sass";
import panini from "panini";
import del from "del";
import browserify from "browserify";
import babelify from "babelify";
import source from "vinyl-source-stream";
import logSymbols from "log-symbols";
import BrowserSync from "browser-sync";
import options from "./config.js";

import gulpBg from "gulp-bg";
import {fileURLToPath} from 'url';
const __filename = fileURLToPath(import.meta.url);

const __dirname = path.dirname(__filename);



 
let bgtask = gulpBg("node", "--harmony", "server.js");

const exitCallback = (proc) => { if (proc.errorcode != 0) { process.exit(proc.errorcode); } };
 
gulp.task("stop", () => {
    bgtask.setCallback(exitCallback);
    bgtask.stop();
  }
);
 


const { src, dest, watch, series, parallel } = gulp;
const browserSync = BrowserSync.create();
var reload = browserSync.reload;
const nodepath = __dirname+"/node_modules/";
const sass = gulpSass(sassCompiler);

function livePreview(done) {
  browserSync.init( 
  {     
    server: {
      baseDir: options.paths.dist.base,
    },
    port:  443,
    open: false,
    logLevel: "silent",
    reloadOnRestart: true,
  });
  done();
}

//Copy latest installed Bulma
function setupBulma() {
  console.log("\n\t" + logSymbols.info, "Installing Bulma Files..\n");
  return src([nodepath + "bulma/*.sass", nodepath + "bulma/**/*.sass"]).pipe(
    dest("./sass/")
  );
}



//Triggers Browser reload
function previewReload(done) {
  console.log(logSymbols.info, "Reloading Browser Preview.");
  browserSync.reload();
  done();
}


// Let's write our task in a function to keep things clean
function javascriptBuild() {
  // Start by calling browserify with our entry pointing to our main javascript file
  return (
    browserify({
      entries: [`${options.paths.src.js}/main.js`],
      // Pass babelify as a transform and set its preset to @babel/preset-env
      transform: [babelify.configure({ presets: ["@babel/preset-env"] })],
    })
      // Bundle it all up!
      .bundle()
      // Source the bundle
      .pipe(source("bundle.js"))
      // Then write the resulting files to a folder
      .pipe(dest(`./dist/js`))
  );
}




function copyFonts() {
  console.log(logSymbols.info, "Copying fonts to dist folder.");
  return src(["./fonts/*"])
    .pipe(dest("./dist/fonts/"))
    .pipe(browserSync.stream());
}


function devClean() {
  console.log(logSymbols.info, "Cleaning dist folder for fresh start.");
  return del([options.paths.dist.base]);
}




//Compile Scss code
function compileSCSS() {
  console.log(logSymbols.info, "Compiling App SCSS..");
  return src(["./scss/main.scss"])
    .pipe(
      sass({
        outputStyle: "compressed",
        sourceComments: "map",
        sourceMap: "scss",
        // includePaths: bourbon,
      }).on("error", sass.logError)
    )
    .pipe(autoprefixer("last 2 versions"))
    .pipe(dest("./dist/css"))
    .pipe(browserSync.stream());
}

//Concat JS
function concatJs() {
  console.log(logSymbols.info, "Compiling Vendor Js..");
  return src(["./js/*"])
    .pipe(sourcemaps.init())
    .pipe(concat("app.js"))
    .pipe(sourcemaps.write("./"))
    .pipe(dest("./dist/js"))
    .pipe(browserSync.stream());
}


//Concat CSS Plugins
function concatCssPlugins() {
  console.log(logSymbols.info, "Compiling Plugin styles..");
  return src([
    nodepath + "simplebar/dist/simplebar.min.css",
    nodepath + "plyr/dist/plyr.css",
    nodepath + "codemirror/lib/codemirror.css",
    nodepath + "codemirror/theme/shadowfox.css",
    "./vendor/css/*",
  ])
    .pipe(sourcemaps.init())
    .pipe(concat("app.css"))
    .pipe(sourcemaps.write("./"))
    .pipe(dest("./dist/css"))
    .pipe(browserSync.stream());
}


//Reset Panini Cache
function resetPages(done) {
  console.log(logSymbols.info, "Clearing Panini Cache..");
  panini.refresh();
  done();
}



//Copy images
function copyImages() {
  return src(`${options.paths.src.img}/**/*`).pipe(
    dest(options.paths.dist.img)
  );
}



//Optimize images
function optimizeImages() {
  return src(`${options.paths.src.img}/**/*`)
    .pipe(imagemin())
    .pipe(dest(options.paths.dist.img));
}


function watchFiles() {
  watch(["./scss/**/*", "./scss/*"], compileSCSS);
  watch(
    `${options.paths.src.js}/**/*.js`,
    series(javascriptBuild, previewReload)
  ).on("change", reload);
  watch(["server.js"], bgtask);
  watch(
    `${options.paths.src.fonts}/**/*`,
    series(copyFonts, previewReload)
  ).on("change", reload);
  watch(`${options.paths.src.img}/**/*`, series(copyImages, previewReload)).on("change", reload);
  console.log(logSymbols.info, "Watching for Changes..");
  
}

const buildTasks = [
  devClean,
  resetPages,
  parallel(
    concatJs,
    copyFonts,
    concatCssPlugins,
    compileSCSS,
    javascriptBuild,
    
  ),
];

export const build = (done) => {
  series( devClean,resetPages, parallel(...buildTasks, optimizeImages))();
  done();
};

export default (done) => {
  series(
    devClean,
    resetPages,
    parallel(...buildTasks, copyImages),
    //parallel(livePreview,watchFiles) //un-comment for local development  || comment in GitHub Repository
    
  )();
  done();
};

export const setup = () => {
  series(setupBulma);
};

