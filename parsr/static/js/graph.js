var Graph;

(function() {

    Graph = Component.extend({

        init: function(base, target, attrs) {
            attrs = attrs || {};

            this.margins = this.createMargins(attrs.margins || {});

            this.width = attrs.width || $(target).width();
            this.height = attrs.height || 400;

            this._super(base, target);
        },

        createMargins: function(margins) {
            return {
                top: margins.top || 0,
                left: margins.left || 0,
                bottom: margins.bottom || 0,
                right: margins.right || 0
            };
        },

        getInnerWidth: function() {
            return this.width - this.margins.left - this.margins.right;
        },

        getInnerHeight: function() {
            return this.height - this.margins.top - this.margins.bottom;
        }

    });

}());
