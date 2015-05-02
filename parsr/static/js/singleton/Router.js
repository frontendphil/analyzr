define([
    "backbone",
    "react",
    "underscore"
], function(
    Backbone,
    React,
    _
) {
    var Router = Backbone.Router.extend({
        routes: {
            "repository/:id": "repository",
            "repository/:id/branch/:bid": "repository",
            "repository/:id/branch/:bid/:lang": "repository",

            "repository/create": "repository_create",

            "login(?*next)": "login",

            "*default": "repositories"
        },

        render: function(View, props) {
            props = props || {};

            require(["jquery", "jsx!views/Main"], function($, Main) {
                props = _.extend(props, {
                    currentView: View
                });

                React.render(
                    React.createElement(Main, props),
                    $("body").get(0)
                );
            });
        },

        repositories: function() {
            require([
                "collections/RepositoryCollection",

                "jsx!views/repository/ListView"
            ], function(
                RepositoryCollection,

                ListView
            ) {
                this.render(ListView, {
                    collection: new RepositoryCollection()
                });
            }.bind(this));
        },

        repository: function(id, bid, lang) {
            require([
                "models/Repository",
                "models/Branch",

                "jsx!views/repository/View"
            ], function(
                Repository,
                Branch,

                View
            ) {
                var branch;

                if(bid) {
                    branch = new Branch({ id: bid });
                }

                this.render(View, {
                    model: new Repository({ id: id }),
                    branch: branch,
                    language: lang
                });
            }.bind(this));
        },

        login: function(next) {
            require([
                "jsx!views/Login"
            ], function(
                Login
            ) {
                this.render(Login);
            }.bind(this));
        }
    });

    return new Router();
});
