require([
    "config"
], function() {
    require([
        // Backbone init
        "backbone",
        "backbone-uniquemodel",
        "backbone-relations"
    ], function() {
        require([
            "singleton/Router"
        ], function(
            Router
        ) {
            if(!Backbone.History.started) {
                Backbone.history.start({
                    pushState: true
                });
            }
        });
    });
});
