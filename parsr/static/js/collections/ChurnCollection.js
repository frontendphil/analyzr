define([
    "backbone",

    "models/Churn"
], function(
    Backbone,

    Churn
) {

    return Backbone.Collection.extend({

        model: Churn,

        getAdditions: function() {
            return [];
        },

        getDeletions: function() {
            return [];
        }

    });

});
