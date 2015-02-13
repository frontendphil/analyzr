require([
    "config"
], function() {
    require([
        "jquery"
    ], function(
        $
    ) {
        $.ajaxSetup({
            contentType:"application/json; charset=utf-8",
            cache: false
        });

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
