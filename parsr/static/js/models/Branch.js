define([
    "backbone",

    "models/Activity",

    "collections/ContributorCollection",
    "collections/ChurnCollection"
], function(
    Backbone,

    Activity,

    ContributorCollection,
    ChurnCollection
) {

    return Backbone.UniqueModel(Backbone.Model.extend({

        embeddings: {
            contributors: ContributorCollection,
            churn: ChurnCollection,
            activity: Activity
        },

        defaults: {
            contributors: [],
            churn: [],

            activity: {}
        },

        isAnalyzed: function() {
            return this.get("analyze") && this.get("analyze").finished;
        },

        isMeasured: function() {
            return this.get("measure") && this.get("measure").finished;
        }

    }), "Branch");

});
