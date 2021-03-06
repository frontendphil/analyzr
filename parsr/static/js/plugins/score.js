ns("plugins");

(function() {

    analyzr.plugins.Score = analyzr.core.Component.extend({

        init: function(target) {
            this._super("score", target);
        },

        clear: function() {
            this.dom.html("");
        },

        createFilter: function(info) {
            var select = $(
                "<select>"+
                    "<option value='all'>All</option>" +
                "</select>"
            );

            $.each(info.languages, function() {
                select.append($(
                    "<option value='" + this +"'>" + this + "</option>"
                ));
            });

            if(info.options.language) {
                select.val(info.options.language);
            }

            return select;
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

            var keys = d3.keys(data.statistics);

            $.each(keys, function(index) {
                if(row && index !== 0 && index % entries === 0) {
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

                if(index === keys.length - 1) {
                    rows.push(row);
                }
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

            var filter = this.createFilter(response.info);
            filter.change(function() {
                var language = "";
                var select = $(this);

                if(select.val() !== "all") {
                    language = "?language=" + select.val();
                }

                that.setup(that.url + language, that.branch);
            });

            this.dom.append(filter);

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
