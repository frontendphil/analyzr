ns("core");

(function() {

    var initializing = false;
    var fnTest;

    // Test if browser supports function decomposition
    if(/xyz/.test(function() { xyz; })) {
        fnTest = /\b_super\b/;
    } else {
        fnTest = /.*/;
    }

    analyzr.core.Class = function() {};
    analyzr.core.Class.extend = function(base) {
        var _super = this.prototype;

        initializing = true;
        var proto = new this();
        initializing = false;

        for(var prop in base) {
            if(typeof base[prop] === "function" &&
                typeof _super[prop] === "function" &&
                fnTest.test(base[prop])) {

                proto[prop] = (function(prop, fn) {
                    return function() {
                        var tmp = this._super;

                        this._super = _super[prop];

                        var ret = fn.apply(this, arguments);
                        this._super = tmp;

                        return ret;
                    };
                })(prop, base[prop]);
            } else {
                proto[prop] = base[prop];
            }
        }

        function Class() {
            if(!initializing && this.init) {
                this.init.apply(this, arguments);
            }
        }

        Class.prototype = proto;
        Class.prototype.constructor = Class;
        Class.extend = arguments.callee;

        return Class;
    };

}());
