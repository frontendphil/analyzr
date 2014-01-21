ns("plugins");

(function() {

    var LINE_COUNT = 5;

    analyzr.plugins.FileStatistics = analyzr.core.Component.extend({

        init: function(target) {
            this.start = {
                h: 50,
                s: 45,
                l: 60
            };

            this.end = 360;
            this.current = this.start.h;

            this._super("stats", target);
        },

        getColor: function(steps) {
            var step = (this.end - this.start.h) / steps;

            this.current = this.current + step;

            return "hsl(" + this.current + "," + this.start.s + "%," + this.start.l + "%)";
        },

        round: function(number) {
            return Math.round(number * 10000) / 100;
        },

        getType: function(mimetype) {
            var index = mimetype.indexOf("/");

            return mimetype.slice(index + 1);
        },

        handleData: function(response) {
            var legend = $("<div class='legend' />");
            var parts = $("<div class='parts' />");

            this.dom.append(parts, legend);

            var line;
            var statistics = [];

            $.each(response.data, function(mimetype, share) {
                statistics.push({
                    mimetype: mimetype,
                    share: share
                });
            });

            statistics = statistics.sort(function(a, b) {
                return a.share - b.share;
            });

            var that = this;

            $.each(statistics, function(index) {
                if(index % LINE_COUNT === 0) {
                    line = $("<div class='line' />");

                    legend.append(line);
                }

                var color = that.getColor(statistics.length);

                var container = $("<div class='stat'>");

                var entry = $("<div class='entry'/>");
                var share = $("<div class='share'>" + that.round(this.share) + "%</div>");
                var type = $("<div class='type'>" + that.getType(this.mimetype) + "</div>");

                var box = $("<div class='box' />");

                box.css({
                    background: color,
                    borderColor: color,
                    borderStyle: "solid",
                    borderWidth: 0
                });

                entry.css({
                    width: (100 / statistics.length) + "%"
                });

                entry.append(box, share, type);
                line.append(entry);

                container.css({
                    width: 100 * this.share + "%",
                    background: color,
                    borderColor: color,
                    borderStyle: "solid",
                    borderWidth: 0
                });

                parts.append(container);
            });

            if(window.matchMedia) {
                window.matchMedia("print").addListener(function(media) {
                    if(media.matches) {
                        that.handlePrint();
                    } else {
                        $(document).one("mousemove", function() {
                            that.handleAfterPrint();
                        });
                    }
                });
            }
        },

        handlePrint: function() {
            this.dom.find(".stat").each(function() {
                var stat = $(this);
                var height = stat.height();

                stat.css({
                    borderWidth: Math.ceil(height/2)
                });
            });

            this.dom.find(".box").each(function() {
                var box = $(this);
                var width = box.width();

                box.css({
                    borderWidth: Math.ceil(width/2)
                });
            });
        },

        handleAfterPrint: function() {
            this.dom.find(".stat").each(function() {
                $(this).css({
                    borderWidth: 0
                });
            });

            this.dom.find(".box").each(function() {
                $(this).css({
                    borderWidth: 0
                });
            });
        }

    });
}());
