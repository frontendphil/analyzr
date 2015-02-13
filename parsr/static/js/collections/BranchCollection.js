define([
    "backbone",
    "underscore",

    "models/Branch"
], function(
    Backbone,
    _,

    Branch
) {

    return Backbone.Collection.extend({

        url: function() {
            return "/branches";
        },

        model: Branch,

        lastUpdated: function() {
            var groups = this.groupBy(function(branch) {
                if(branch.isAnalyzed()) {
                    return "analyzed";
                }

                if(branch.isMeasures()) {
                    return "measured";
                }

                return "rest";
            });

            if(groups.measured) {
                return groups.measured[0];
            }

            if(groups.analyzed) {
                return groups.analyzed[0];
            }
        },

    });

});
