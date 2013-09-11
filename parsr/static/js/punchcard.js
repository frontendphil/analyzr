var Punchcard;

(function() {

    var WEEKDAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ];

    Punchcard = Class.extend({

        init: function(attrs) {
            this.dom = $(attrs.renderTo);

            var repo = this.dom.attr("repo");
            var author = this.dom.attr("author");

            var url = "/punchcard/repo/" + repo;

            if(author) {
                url = url + "/author/" + author;
            }

            this.setup(url);
        },

        setup: function(url) {
            var that = this;

            $.ajax(url, {
                success: function(data) {
                    var table = $("<table class='table' />");

                    that.createHeader(table);

                    var container = $("<tbody></tbody>");
                    table.append(container);

                    $.each(WEEKDAYS, function(day) {
                        var dayContainer = $(
                            "<tr>" +
                                "<td class='day'>" + WEEKDAYS[day] + "</td>" +
                            "</tr>"
                        );

                        for(var hour = 0; hour < 24; hour = hour + 1) {
                            var hourContainer = $("<td class='hour' />");

                            if(data[day]) {
                                hourContainer.append(that.createCircle(data[day][hour], data.max));
                            }

                            dayContainer.append(hourContainer);
                        }

                        container.append(dayContainer);
                    });

                    that.dom.append(table);
                }
            });
        },

        createCircle: function(value, max) {
            var container = $("<div class='circle' />");

            if(!value) {
                return container;
            }

            value = value / max;

            return container.css({
                width: 20 * value,
                height: 20 * value
            });
        },

        createHeader: function(table) {
            var container = $("<thead />");
            var head = $("<tr><th>Day</th></tr>");

            container.append(head);

            for(var hour = 0; hour < 24; hour = hour + 1) {
                head.append("<th>" + hour + "</th>");
            }

            table.append(container);
        }

    });

    Punchcard.auto = function() {
        $(".punchcard").each(function() {
            new Punchcard({
                renderTo: this
            });
        });
    };

}());
