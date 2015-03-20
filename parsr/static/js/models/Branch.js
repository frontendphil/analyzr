define([
    "backbone",

    "models/Activity",

    "collections/ContributorCollection"
], function(
    Backbone,

    Activity,

    ContributorCollection
) {

    return Backbone.UniqueModel(Backbone.Model.extend({

        embeddings: {
            contributors: ContributorCollection,
            activity: Activity
        },

        defaults: {
            contributors: [],

            activity: {}
        },

        isAnalyzed: function() {
            return this.get("analyze") && this.get("analyze").finished;
        },

        isMeasured: function() {
            return this.get("measre") && this.get("measure").finished;
        }

    }), "Branch");

});
