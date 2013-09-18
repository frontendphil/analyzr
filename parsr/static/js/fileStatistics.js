var FileStatistics;

(function() {

    FileStatistics = Class.extend({

        init: function(target) {
            this.dom = $(target);

            var repo = this.dom.attr("repo");
            var author = this.dom.attr("url");

            var url = "/file_stats/repo/" + repo;

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

                    $.each(statistics, function() {
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
                        legend.append(entry);

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
