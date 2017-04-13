var path = require("path"),
    L = require("partial.lenses");

// eg. add_noprint_suffix("dist/css/foo.min.css") => "dist/css/foo-noprint.min.css"
function add_noprint_suffix(path_str) {
  var parts = path.parse(path_str);
  var i = parts.name.indexOf(".");
  if (i !== -1)
    parts.name = parts.name.slice(0, i) + "-noprint" + parts.name.slice(i);
  else
    parts.name += "-noprint";
  return path.format({
    dir: parts.dir,
    base: parts.name+parts.ext
  });
}

// extract from src using lens_src, then apply transform, then set lens_dest to it
// the result is curried, call it with the destination
function mapping_on(src, lens_src, lens_dest, transform) {
  return L.set(lens_dest, transform(L.get(lens_src, src)));
}

// left-to-right function composition (1-arity): pipe(f, g)(x) == g(f(x))
function pipe() {
  var args = Array.prototype.slice.apply(arguments);
  return function(x) {
    for (var i = 0; i < args.length; i++)
      x = args[i](x);
    return x;
  }
}

module.exports = function(grunt) {
  var dir_dest = __dirname+"/"; // vendor/bootstrap
  var dir_bootstrap = process.cwd(); // node_modules/bootstrap

  require(path.join(dir_bootstrap, "Gruntfile.js"))(grunt);

  var bootstrap_config = grunt.config.get();

  grunt.config.merge({
    copy: {
      noPrintLess: {
        src: "less/bootstrap.less",
        dest: "less/bootstrap-noprint.less",
        options: {
          process: function(content, srcpath) {
            return content.replace('@import "print.less"', "");
          }
        }
      },
      noPrintDist: {
        src: "dist/css/bootstrap-noprint.*",
        dest: dir_dest
      }
    }
  });

  var mimic_bootstrap_targets = pipe(
    // [lens, ...] is shorthand for L.compose(lens, ...)
    mapping_on(bootstrap_config, [L.prop("less"), L.prop("compileCore")], [L.prop("less"), L.prop("compileNoPrint")],
      pipe(L.set(L.prop("src"), "less/bootstrap-noprint.less"),
           L.modify(L.prop("dest"), add_noprint_suffix),
           L.modify(L.prop("options"),
             pipe(L.modify(L.prop("sourceMapURL"), add_noprint_suffix),
                  L.modify(L.prop("sourceMapFilename"), add_noprint_suffix))))),
    mapping_on(bootstrap_config, [L.prop("autoprefixer"), L.prop("core")], [L.prop("autoprefixer"), L.prop("noPrint")],
      L.modify(L.prop("src"), add_noprint_suffix)),
    mapping_on(bootstrap_config, [L.prop("cssmin"), L.prop("minifyCore")], [L.prop("cssmin"), L.prop("minifyNoPrint")],
      pipe(L.modify(L.prop("src"), add_noprint_suffix),
           L.modify(L.prop("dest"), add_noprint_suffix))),
    mapping_on(bootstrap_config, [L.prop("csscomb"), L.prop("dist")], [L.prop("csscomb"), L.prop("noPrint")],
      L.set(L.prop("src"), "*-noprint.css")));
  grunt.config.merge(mimic_bootstrap_targets({}));

  grunt.registerTask("less-compileNoPrint", ["copy:noPrintLess", "less:compileNoPrint"])

  grunt.registerTask('noprint-css', ['less-compileNoPrint', 'autoprefixer:noPrint', 'csscomb:noPrint', 'cssmin:minifyNoPrint', 'copy:noPrintDist']);
};
