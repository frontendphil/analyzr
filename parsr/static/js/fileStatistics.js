var FileStatistics;

(function() {

    var LINE_COUNT = 5;

    FileStatistics = Class.extend({

        init: function(target) {
            this.dom = $(target);

            var branch = this.dom.data("branch");
            var author = this.dom.data("author");

            var url = "/file_stats/branch/" + branch;

            if(author) {
                url = url + "/author/" + author;
            }

            this.setup(url);
        },

        setup: function(url) {
            var that = this;

            var start = {
                h: 50,
                s: 45,
                l: 60
            };

            var end = 360;
            var current = start.h;

            var getColor = function(steps) {
                var step = (end - start.h) / steps;

                current = current + step;

                return "hsl(" + current + "," + start.s + "%," + start.l + "%)";
            };

            var round = function(number) {
                return Math.round(number * 10000) / 100;
            };

            var getType = function(mimetype) {
                var index = mimetype.indexOf("/");

                return mimetype.slice(index + 1);
            };

            $.ajax(url, {
                success: function(statistics) {
                    var legend = $("<div class='legend' />");
                    var parts = $("<div class='parts' />");

                    that.dom.append(parts, legend);

                    var line;

                    $.each(statistics, function(index) {
                        if(index % LINE_COUNT === 0) {
                            line = $("<div class='line' />");

                            legend.append(line);
                        }

                        var color = getColor(statistics.length);

                        var container = $("<div class='stat'>");

                        var entry = $("<div class='entry'/>");
                        var share = $("<div class='share'>" + round(this.share) + "%</div>");
                        var type = $("<div class='type'>" + getType(this.mimetype) + "</div>");

                        var box = $("<div class='box' />");

                        box.css({
                            background: color
                        });

                        entry.css({
                            width: (100 / statistics.length) + "%"
                        });

                        entry.append(box, share, type);
                        line.append(entry);

                        container.css({
                            width: 100 * this.share + "%",
                            background: color
                        });

                        parts.append(container);
                    });
                }
            });
        }

    });

    FileStatistics.auto = function(target) {
        $(target || ".statistics").each(function() {
            new FileStatistics(this);
        });
    };

}());
