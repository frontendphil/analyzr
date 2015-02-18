define([
    "backbone",

    "collections/ContributorCollection"
], function(
    Backbone,

    ContributorCollection
) {

    return Backbone.UniqueModel(Backbone.Model.extend({

        embeddings: {
            contributors: ContributorCollection
        },

        defaults: {
            contributors: []
        },

        isAnalyzed: function() {
            return this.get("analyze") && this.get("analyze").finished;
        },

        isMeasured: function() {
            return this.get("measre") && this.get("measure").finished;
        }

    }), "Branch");

});
