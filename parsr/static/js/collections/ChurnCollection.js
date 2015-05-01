define([
    "backbone",

    "models/Churn"
], function(
    Backbone,

    Churn
) {

    return Backbone.Collection.extend({

        model: Churn

    });

});
