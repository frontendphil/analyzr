ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.StructuralMetrics = analyzr.plugins.graph.metrics.MetricsBase.extend({

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
