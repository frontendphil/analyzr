ns("core");

(function() {

    var _toArray = function(list) {
        var i, length;
        var result = [];

        for(i = 0, length = list.length; i < length; i = i + 1) {
            result.push(list[i]);
        }

        return result;
    };

    analyzr.core.Observable = analyzr.core.Class.extend({

        init: function() {
            this.listeners = {};
        },

        on: function(event, callback) {
            if(!this.listeners[event]) {
                this.listeners[event] = [];
            }

            this.listeners[event].push(callback);
        },

        un: function(event, callback) {
            if(!callback) {
                this.listeners[event] = [];
            }

            if(!this.listeners[event] || this.listeners[event].indexOf(callback) === -1) {
                return;
            }

            var index = this.listeners[event].indexOf(callback);

            var l = this.listeners[event];

            this.listeners[event] = l.splice(0, index).concat(l.splice(index));
        },

        raise: function() {
            var args = _toArray(arguments);
            var event = args.shift();

            if(!this.listeners[event]) {
                return;
            }

            var that = this;

            $.each(this.listeners[event], function() {
                this.apply(that, args);
            });
        }

    });

}());
