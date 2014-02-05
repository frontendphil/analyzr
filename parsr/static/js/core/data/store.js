ns("core.data");

(function (){

    var STORES = {};
    var LOADING = {};

    analyzr.core.data = {

        get: function(url, options) {
            if(!options.update && STORES[url]) {
                window.setTimeout(function() {
                    options.success(STORES[url]);
                }, 1);

                return;
            }

            if(LOADING[url]) {
                LOADING[url].push(options);

                return;
            }

            LOADING[url] = [options];

            var applyCallback = function(url, name) {
                return function() {
                    var args = arguments;

                    $.each(LOADING[url], function() {
                        var clb = this[name];

                        if(!clb) {
                            return;
                        }

                        clb.apply(this, args);
                    });

                    delete LOADING[url];
                };
            };

            $.ajax(url, {
                success: function(response) {
                    STORES[url] = response;

                    applyCallback(url, "success")(response);
                },
                error: applyCallback(url, "error")
            });
        }

    };

}());
