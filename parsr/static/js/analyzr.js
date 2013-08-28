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

    $(document).ready(function() {
        $(".analyze").click(function() {
            var rel = $(this).attr("rel");

            $.ajax(rel, {
                type: "POST",
                beforeSend: function() {
                    window.setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                },
                data: {
                    csrfmiddlewaretoken: $.cookie("csrftoken")
                }
            });

            return false;
        });

        $(".punchcard").each(function() {
            var punchard = $(this);

            var repo = punchard.attr("repo");
            var author = punchard.attr("author");

            var url = "/punchcard/repo/" + repo;

            if(author) {
                url = url + "/author/" + author;
            }

            var createHeader = function(table) {
                var container = $("<thead />");
                var head = $("<tr><th>Day</th></tr>");

                container.append(head);

                for(var hour = 0; hour < 24; hour = hour + 1) {
                    head.append("<th>" + hour + "</th>");
                }

                table.append(container);
            };

            var createCircle = function(value, max) {
                var container = $("<div class='circle' />");

                if(!value) {
                    return container;
                }

                value = value / max;

                return container.css({
                    width: 20 * value,
                    height: 20 * value
                });
            };

            $.ajax(url, {
                success: function(data) {
                    var table = $("<table class='table' />");

                    createHeader(table);

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
                                hourContainer.append(createCircle(data[day][hour], data.max));
                            }

                            dayContainer.append(hourContainer);
                        }

                        container.append(dayContainer);
                    });

                    punchard.append(table);
                }
            });
        });
    });
}());
