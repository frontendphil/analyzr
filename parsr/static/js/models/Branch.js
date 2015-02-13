define([
    "backbone"
], function(
    Backbone
) {

    return Backbone.UniqueModel(Backbone.Model.extend({

        url: function() {
            return "api/branch";
        },

        isAnalyzed: function() {
            return this.get("analyze") && this.get("analyze").finished;
        },

        isMeasured: function() {
            return this.get("measre") && this.get("measure").finished;
        }

    }), "Branch");

});
