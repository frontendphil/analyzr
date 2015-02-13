require.config({

    baseUrl: "/static/js",

    paths: {
        "requireLib": "../vendor/bower/requirejs/require",
        "text": "../vendor/bower/requirejs-text/text",

        "underscore": "../vendor/bower/lodash/dist/lodash.min",

        "react": "../vendor/bower/react/react-with-addons",
        "jsx": "../vendor/bower/requirejs-jsx-plugin/js/jsx",
        "JSXTransformer": "../vendor/bower/requirejs-jsx-plugin/js/JSXTransformer",
        "react-bootstrap": "../vendor/bower/react-bootstrap",

        "backbone-base": "../vendor/bower/backbone/backbone",
        "backbone-relations": "../vendor/bower/backbone-relations/backbone-relations",
        "backbone": "../vendor/bower/backbone.uniquemodel/backbone.uniquemodel",

        "jquery": "../vendor/bower/jquery/dist/jquery.min"
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
