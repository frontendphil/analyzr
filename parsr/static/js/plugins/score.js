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
                "<table class='table table-bordered'>" +
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

        createStatistics: function(data, size) {
            var entries = 3;
            var rows = [];
            var row;

            $.each(d3.keys(data.statistics), function(index) {
                if(row && index % entries === 0) {
                    rows.push(row);
                    row = null;
                }

                if(!row) {
                    row = {
                        headers: [],
                        values: []
                    };
                }

                var key = this.toString();
                var value = data.statistics[key];

                row.headers.push(key.capitalize());
                row.values.push(value.toFixed(2));
            });

            var createTable = function(headers, values) {
                return $(
                    "<table class='table'>" +
                        "<thead>" +
                            $.map(headers, function(value) {
                                return "<th>" + value + "</th>";
                            }).join("") +
                        "</thead>" +
                        "<tbody>" +
                            "<tr>" +
                                $.map(values, function(value) {
                                    return "<td>" + value + "</td>";
                                }).join("") +
                            "</tr>" +
                        "</tbody>" +
                    "</table>"
                );
            };

            var container = $(
                "<tr>" +
                    "<td class='statistics' colspan='" + size + "'></td>" +
                "</tr>"
            );

            $.each(rows, function() {
                container.find("> td").append(createTable(this.headers, this.values));
            });

            return container;
        },

        handleData: function(response) {
            this.clear();

            var fields = response.info.keys.sort();
            var metrics = [];

            $.each(response.data, function(key) {
                metrics.push(key);
            });

            var that = this;

            $.each(metrics.sort(), function() {
                var table = that.createTable(fields);
                var body = table.find("tbody");

                var key = this.toString();
                var metric = response.data[key];
                var row = $("<tr />");

                row.append($("<td rowspan='2'>" + key.capitalize() + "</td>"));

                $.each(fields, function() {
                    var key = this.toString();

                    row.append($("<td>" + metric[key].toFixed(2) + "</td>"));
                });

                var stats = that.createStatistics(response.data[key], fields.length);

                body.append(row, stats);

                that.dom.append(table);
            });
        }

    });

}());
