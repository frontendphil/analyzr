require.config({

    baseUrl: "/static/js",

    paths: {
        "requireLib": "../vendor/bower/requirejs/require",
        "text": "../vendor/bower/requirejs-text/text",

        "underscore": "../vendor/bower/lodash/dist/lodash.min",

        "react": "../vendor/bower/react/react-with-addons.min",
        "jsx": "../vendor/bower/requirejs-jsx-plugin/js/jsx",
        "JSXTransformer": "../vendor/bower/requirejs-jsx-plugin/js/JSXTransformer-0.10.0",
        "react-bootstrap": "../vendor/bower/react-bootstrap",

        "backbone": "../vendor/bower/backbone/backbone",
        "backbone-ext": "extensions/backbone",
        "backbone-uniquemodel": "../vendor/bower/backbone.uniquemodel/backbone.uniquemodel",
        "backbone-relational": "../vendor/bower/backbone-relational/backbone-relational",
        "backbone-react": "../vendor/bower/backbone-react-component/lib/component",

        "jquery": "../vendor/bower/jquery/dist/jquery.min"
    },

    jsx: {
        fileExtension: ".jsx"
    }
});
