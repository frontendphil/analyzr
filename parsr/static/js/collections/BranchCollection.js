define([
    "backbone",

    "models/Branch"
], function(
    Backbone,

    Branch
) {

    return Backbone.Collection.extend({

        url: function() {
            return this.repository.url() + "/branches";
        },

        model: Branch

    });

});
