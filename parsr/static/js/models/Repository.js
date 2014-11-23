define([
    "backbone",

    "models/Branch",

    "collections/BranchCollection"
], function(
    Backbone,

    Branch,

    BranchCollection
) {
    return Backbone.UniqueModel(Backbone.RelationalModel.extend({

        relations: [
            {
                type: Backbone.HasMany,
                key: "branches",
                relatedModel: Branch,
                collectionType: BranchCollection,
                reverseRelation: {
                    key: "repository"
                }
            }
        ]

    }));
});
