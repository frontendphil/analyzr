ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.Structure = analyzr.plugins.graph.metrics.Metric.extend({

        init: function(target, attrs) {
            attrs = attrs || {};

            attrs.title = attrs.title || "Structural Metrics";

            this._super(target, attrs);
        },

        getKind: function() {
            return "structure";
        }

    });

}());
