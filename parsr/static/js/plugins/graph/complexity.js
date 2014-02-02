ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.ComplexityMetrics = analyzr.plugins.graph.metrics.MetricsBase.extend({

        init: function(target, attrs) {
            attrs = attrs || {};

            attrs.title = attrs.title || "Complexity Metrics";

            this._super(target, attrs);
        },

        getKind: function() {
            return "complexity";
        }

    });

}());
