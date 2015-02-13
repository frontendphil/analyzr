define([
    "backbone",

    "models/Branch",

    "collections/BranchCollection"
], function(
    Backbone,

    Branch,

    BranchCollection
) {
    return Backbone.UniqueModel(Backbone.Model.extend({

        references: {
            branch: Branch
        }

    }), "Repository");
});
