ns("plugins");

(function() {

    analyzr.plugins.Score = analyzr.core.Component.extend({

        init: function(target) {
            this._super("score", target);
        },

        clear: function() {
            this.dom.html("");
        },

        createTable: function(columns) {
            var table = $(
                "<table class='table table-bordered table-hover'>" +
                    "<thead>" +
                        "<tr></tr>" +
                    "</thead>" +
                    "<tbody></tbody>" +
                "</table>"
            );

            columns = ["metric"].concat(columns);

            var row = table.find("tr");

            $.each(columns, function() {
                row.append($("<th>" + this.capitalize() + "</th>"));
            });

            return table;
        },

        handleData: function(response) {
            this.clear();

            var fields = response.info.keys.sort();
            var metrics = [];

            $.each(response.data, function(key) {
                metrics.push(key);
            });

            var table = this.createTable(fields);
            var body = table.find("tbody");

            $.each(metrics.sort(), function() {
                var key = this.toString();
                var metric = response.data[key];
                var row = $("<tr />");

                row.append($("<td>" + key.capitalize() + "</td>"));

                $.each(fields, function() {
                    var key = this.toString();

                    row.append($("<td>" + metric[key].toFixed(2) + "</td>"));
                });

                body.append(row);
            });

            this.dom.append(table);
        }

    });

}());
