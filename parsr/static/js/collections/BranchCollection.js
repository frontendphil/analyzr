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

        urlSuffix: "/branches",

        model: Branch,

        lastUpdated: function() {
            var groups = this.groupBy(function(branch) {
                if(branch.isAnalyzed()) {
                    return "analyzed";
                }

                if(branch.isMeasured()) {
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

            return this.at(0);
        },

    });

});
