ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.StructuralMetrics = analyzr.plugins.graph.metrics.MetricsBase.extend({

        getKind: function() {
            return "structure";
        }

    });

}());
