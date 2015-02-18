define([
    "backbone",

    "models/Contributor"
], function(
    Backbone,

    Contributor
) {

    return Backbone.Collection.extend({

        model: Contributor

    });

});
