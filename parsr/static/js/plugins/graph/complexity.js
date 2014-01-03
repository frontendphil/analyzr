ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.ComplexityMetrics = analyzr.plugins.graph.metrics.MetricsBase.extend({

        getKind: function() {
            return "complexity";
        }

    });

}());
