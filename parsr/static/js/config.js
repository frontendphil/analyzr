require.config({

    baseUrl: "/static/js",

    paths: {
        "requireLib": "../vendor/bower/requirejs/require",
        "text": "../vendor/bower/requirejs-text/text",

        "underscore": "../vendor/bower/lodash/dist/lodash.min",

        "react": "../vendor/bower/react/react-with-addons.min",
        "jsx": "../vendor/bower/requirejs-jsx-plugin/js/jsx",
        "JSXTransformer": "../vendor/bower/requirejs-jsx-plugin/js/JSXTransformer",
        "react-bootstrap": "../vendor/bower/react-bootstrap",

        "backbone": "../vendor/bower/backbone/backbone",
        "backbone-uniquemodel": "../vendor/bower/backbone.uniquemodel/backbone.uniquemodel",
        "backbone-relations": "../vendor/bower/backbone-relations/backbone-relations",

        "jquery": "../vendor/bower/jquery/dist/jquery.min"
    },

    map: {
        "models": {
            "backbone": "backbone-uniquemodel"
        },

        "backbone-uniquemodel": {
            "backbone": "backbone-relations"
        }
    },

    jsx: {
        fileExtension: ".jsx"
    }
});
