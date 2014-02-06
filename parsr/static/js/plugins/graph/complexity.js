ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.Complexity = analyzr.plugins.graph.metrics.Metric.extend({

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
