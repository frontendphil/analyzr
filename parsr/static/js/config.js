(function() {

    var vendor = function(path) {
        return "../vendor/bower/" + path;
    };

    require.config({

        baseUrl: "/static/js",

        paths: {
            "requireLib": vendor("requirejs/require"),
            "text": vendor("requirejs-text/text"),

            "underscore": vendor("lodash/lodash.min"),

            "react": vendor("react/react-with-addons"),
            "jsx": vendor("requirejs-jsx-plugin/js/jsx"),
            "JSXTransformer": vendor("requirejs-jsx-plugin/js/JSXTransformer"),
            "react-bootstrap": vendor("react-bootstrap"),
            "react-d3": vendor("react-d3-components/dist/react-d3-components"),

            "backbone-base": vendor("backbone/backbone"),
            "backbone-rel": vendor("backbone-rel/backbone-rel"),
            "backbone-react-mixin": vendor("backbone-rel/react-mixin"),
            "backbone": vendor("backbone.uniquemodel/backbone.uniquemodel"),

            "jquery": vendor("jquery/dist/jquery.min"),
            "d3": vendor("d3/d3.min")
        },

        map: {
            "backbone-rel": {
                "backbone": "backbone-base"
            },

            "backbone": {
                "backbone": "backbone-rel"
            }
        },

        jsx: {
            fileExtension: ".jsx",
            harmony: true
        }
    });


}());
