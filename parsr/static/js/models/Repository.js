define([
    "backbone",

    "collections/BranchCollection"
], function(
    Backbone,

    BranchCollection
) {
    return Backbone.UniqueModel(Backbone.Model.extend({

        urlRoot: "/api/repository",

        embeddings: {
            branches: BranchCollection
        },

        defaults: {
            branches: []
        },

        getMostInterestingBranch: function() {
            return this.get("branches").lastUpdated();
        }

    }), "Repository");
});
