ns("plugins");

(function() {

    analyzr.plugins.Legend = analyzr.core.Observable.extend({

        init: function(target, attrs) {
            attrs = attrs || {};

            this._super();

            this.dom = $(target);

            this.render(attrs);
        },

        render: function(attrs) {
            var toggle = $("<a href='#'>Show legend...</a>");
            var content = $("<div class='content' />");

            var entries = this.createEntries(attrs.values, attrs.color);
            content.append(entries);

            content.hide();

            toggle.click(function() {
                $(this).hide(function() {
                    content.slideDown();
                });

                return false;
            });

            var body = $("<div class='legend' />");
            body.append(toggle, content);

            this.dom.append(body);
        },

        clear: function() {
            this.dom.find(".content").html("");
        },

        update: function(values, color) {
            this.clear();

            var entries = this.createEntries(values, color);
            this.dom.find(".content").append(entries);
        },

        createEntries: function(values, color) {
            var entries = [];

            $.each(values, function() {
                var entry = $("<div class='entry' />");
                var marker = $("<div class='marker' />");
                marker.css({
                    color: color(this)
                });

                entry.append(marker, this);

                entries.push(entry);
            });

            return entries;
        }

    });

}());
