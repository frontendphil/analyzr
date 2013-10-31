var Metrics;

(function() {

    Metrics = Component.extend({

        init: function(target, attrs) {
            attrs = attrs || {};

            this.margins = this.createMargins(attrs.margins || {});

            this.width = attrs.width || $(target).width();
            this.height = attrs.height || 400;

            this._super("metrics", target);
        },

        createMargins: function(margins) {
            return {
                top: margins.top || 0,
                left: margins.left || 0,
                bottom: margins.bottom || 0,
                right: margins.right || 0
            };
        },

        createDiagram: function(data) {
            var x = d3.time.scale().range([0, this.width]);
            var y = d3.scale.linear().range([this.height, 0]);

            var xAxis = d3.svg.axis().scale(x).orient("bottom");
            var yAxis = d3.svg.axis().scale(y).orient("left").tickSize(-this.getInnerWidth());

            var line = d3.svg.line()
                .interpolate("basis")
                .x(function(d) {
                    return x(d.date);
                })
                .y(function(d) {
                    return y(d.value);
                });

            var svg = d3.select(this.dom.get(0)).append("svg")
                .attr("class", "chart")
                .attr("width", this.width)
                .attr("height", this.height + this.margins.top + this.margins.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margins.left + "," + this.margins.top + ")");

            x.domain(d3.extent(data.values, function(d) {
                return d.date;
            }));

            y.domain([
                d3.min(data.values, function(d) {
                    return d.value;
                }),
                d3.max(data.values, function(d) {
                    return d.value;
                })
            ]);

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0, " + this.height + ")")
                .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            var metric = svg.selectAll(".metric")
                .data([data])
                .enter().append("g")
                .attr("class", "metric");

            metric.append("path")
                .attr("class", "line")
                .attr("d", function(d) {
                    return line(d.values);
                });

            svg.append("text")
                .attr("class", "header")
                .attr("dx", -this.margins.left)
                .attr("dy", -(this.margins.top / 2))
                .text(data.type);
        },

        getInnerWidth: function() {
            return this.width - this.margins.left - this.margins.right;
        },

        getInnerHeight: function() {
            return this.height - this.margins.top - this.margins.bottom;
        },

        setup: function(url) {
            var parseDate = d3.time.format("%Y%m%d - %H:%M").parse;

            var that = this;

            d3.json(url, function(error, data) {
                data.forEach(function(d) {
                    d.date = new Date(d.date);
                });

                var metrics = d3.keys(data[0])
                    .sort()
                    .filter(function(key) {
                        return key !== "date";
                    })
                    .map(function(type) {
                        return {
                            type: type,
                            values: data.map(function(d) {
                                return {
                                    date: d.date,
                                    value: d[type]
                                };
                            })
                        };
                });

                metrics.forEach(function(metric) {
                    that.createDiagram(metric);
                });
            });
        }
    });

    Metrics.auto = function(target, attrs) {
        $(target || ".metrics").each(function() {
            new Metrics(this, attrs);
        });
    };

}());
