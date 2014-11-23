define([
    "backbone",

    "models/Repository"
], function(
    Backbone,

    Repository
) {
    return Backbone.Collection.extend({

        url: "/api/repositories",

        model: Repository
    });
});
