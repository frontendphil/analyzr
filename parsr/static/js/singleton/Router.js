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
                    Main(props),
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

        repository: function(id, bid) {
            require([
                "models/Repository",

                "jsx!views/Repository"
            ], function(
                Repository,

                View
            ) {
                this.render(View, {
                    model: new Repository({ id: id }),
                    branchId: bid
                });
            }.bind(this));
        },

        branch: function(id) {
            require([
                "models/Branch",

                "jsx!views/branch/View"
            ], function(
                Branch,

                View
            ) {

                this.render(View, {
                    model: new Branch({ id: id })
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
