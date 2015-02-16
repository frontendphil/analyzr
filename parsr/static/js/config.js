(function() {

    var vendor = function(path) {
        return "../vendor/bower/" + path;
    };

    require.config({

        baseUrl: "/static/js",

        paths: {
            "requireLib": vendor("requirejs/require"),
            "text": vendor("requirejs-text/text"),

            "underscore": vendor("lodash/dist/lodash.min"),

            "react": vendor("react/react-with-addons"),
            "jsx": vendor("requirejs-jsx-plugin/js/jsx"),
            "JSXTransformer": vendor("requirejs-jsx-plugin/js/JSXTransformer"),
            "react-bootstrap": vendor("react-bootstrap"),

            "backbone-base": vendor("backbone/backbone"),
            "backbone-relations": vendor("backbone-relations/backbone-relations"),
            "backbone-react-mixin": vendor("backbone-relations/react-mixin"),
            "backbone": vendor("backbone.uniquemodel/backbone.uniquemodel"),

            "jquery": vendor("jquery/dist/jquery.min")
        },

        map: {
            "backbone-relations": {
                "backbone": "backbone-base"
            },

            "backbone": {
                "backbone": "backbone-relations"
            }
        },

        jsx: {
            fileExtension: ".jsx"
        }
    });


}());
