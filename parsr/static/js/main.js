require([
    "config"
], function() {
    require([
        "backbone",
        "backbone-uniquemodel",

        "singleton/Router"
    ], function(
        Backbone,
        UniqueModel,

        Router
    ) {
        if(!Backbone.History.started) {
            Backbone.history.start({
                pushState: true
            });
        }
    });
});
