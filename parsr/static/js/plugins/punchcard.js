ns("plugins");

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

    analyzr.plugins.Punchcard = analyzr.core.Component.extend({

        init: function(target) {
            this._super("punchcard", target);
        },

        handleData: function(response) {
            var table = $("<table class='table' />");
            var that = this;
            var data = response.data;
            var info = response.info;

            this.createHeader(table);

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
                        hourContainer.append(that.createCircle(data[day][hour], info.options.max));
                    }

                    dayContainer.append(hourContainer);
                }

                container.append(dayContainer);
            });

            this.dom.append(table);
        },

        createCircle: function(value, max) {
            var container = $("<div class='circle' />");

            if(!value) {
                return container;
            }

            container.qtip({
                content: {
                    text: $("<div><b>" + value + "</b> contributions</div>")
                },
                position: {
                    my: "bottom center",
                    at: "top center",
                    adjust: {
                        y: -10
                    }
                },
                style: {
                    classes: "qtip-dark qtip-tipsy qtip-shadow"
                }
            });

            var start = {
                h: 50,
                s: 45,
                l: 60
            };

            var end = 360;

            value = value / max;

            var color = start.h + ((end-start.h) * value);

            container.on("mouseenter", function() {
                $(this).css({
                    border: "1px solid hsl(" + color + "," + start.s + "%," + (start.l - 10) + "%)"
                });
            }).on("mouseleave", function() {
                $(this).css({
                    border: "none"
                });
            });

            return container.css({
                width: 20 * value,
                height: 20 * value,
                background: "hsl(" + color + "," + start.s + "%," + start.l + "%)"
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

}());
