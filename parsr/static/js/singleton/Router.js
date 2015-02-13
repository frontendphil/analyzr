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
            "repository/create": "repository_create",

            "branch/:id": "branch",

            "author/:id": "author",
            "revision/:id": "revision",
            "file/:id": "file",
            "package/:id": "package",

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
                "models/Repository"
            ], function(
                Repository
            ) {
                var repository = new Repository({ id: id });
                debugger;
                var branch = repository.get("branches").lastUpdated();

                this.navigate("/branch/" + branch.id, {
                    trigger: true,
                    replace: true
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
        }
    });

    return new Router();
});
