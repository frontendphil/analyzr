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

    Punchcard = Component.extend({

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

            var start = {
                h: 50,
                s: 45,
                l: 60
            };

            var end = 360;

            value = value / max;

            var color = start.h + ((end-start.h) * value);

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
