ns("plugins.graph");

(function() {

    analyzr.plugins.graph.CodeChurn = analyzr.plugins.graph.Graph.extend({

        init: function(target, attrs) {
            attrs = attrs || {};

            attrs.title = attrs.title || "Code Churn";

            this._super("churn", target, attrs);

            this.svg.append("path")
                .attr("class", "area added");

            this.svg.append("path")
                .attr("class", "area removed");
        },

        handleData: function(svg, response) {
            var data = [];

            this.updateFilters(response.info);

            $.each(response.data, function(date, value) {
                value.date = new Date(date);

                data.push(value);
            });

            this.updateScales(svg, response.info);
            this.updateDiagram(svg, data.sort(function(a, b) {
                return a.date - b.date;
            }));
        },

        updateDiagram: function(svg, data) {
            var that = this;

            var added = d3.svg.area()
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y1(function(d) {
                    return that.scale.y(d.added);
                })
                .y0(function() {
                    return that.scale.y(0);
                });

            svg.selectAll(".area.added")
                .datum(data)
                .attr("d", added);

            var removed = d3.svg.area()
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y1(function() {
                    return that.scale.y(0);
                })
                .y0(function(d) {
                    return that.scale.y(-1 * d.removed);
                });

            svg.selectAll(".area.removed")
                .datum(data)
                .attr("d", removed);
        },

        getMaxValue: function(d) {
            return d.added;
        },

        getMinValue: function(d) {
            return -1 * d.removed;
        }

    });

}());
