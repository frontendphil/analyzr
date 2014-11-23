module.exports = function(grunt) {
    grunt.initConfig({

        pkg: grunt.file.readJSON("package.json"),

        less: {
            default: {
                files: {
                    "parsr/static/stylesheets/css/analyzr.css": "parsr/static/stylesheets/less/analyzr.less"
                }
            }
        },

        watch: {
            less: {
                files: "parsr/static/stylesheets/less/**/*.less",
                tasks: ["less"],
                options: {
                    spawn: false
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
};
