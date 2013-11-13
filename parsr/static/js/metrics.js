var Metrics;

(function() {

    Metrics = Graph.extend({

        init: function(target, attrs) {
            this._super("metrics", target, attrs);
        },

        createMetric: function(svg, data, color, offset) {
            var y = d3.scale.linear().range([this.height, 0]);
            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left");

            var that = this;

            var current = 0;

            data.values.forEach(function(d) {
                current = current + d.value;

                d.value = current;
            });

            var line = d3.svg.line()
                .interpolate("basis")
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y(function(d) {
                    return y(d.value);
                });

            y.domain([
                d3.min(data.values, function(d) {
                    return d.value;
                }),
                d3.max(data.values, function(d) {
                    return d.value;
                })
            ]);

            svg.append("g")
                .attr("class", "y axis axis-" + data.id)
                .attr("transform", "translate(" + offset + ", 0)")
                .call(yAxis);

            var metric = svg.selectAll(".metric." + data.id)
                .data([data])
                .enter().append("g")
                .attr("class", "metric " + data.id);

            metric.append("path")
                .attr("class", "line")
                .attr("d", function(d) {
                    return line(d.values);
                })
                .style("stroke", function(d) {
                    return color(d.id);
                });

            svg.append("text")
                .attr("class", "header")
                .attr("dx", offset)
                .attr("dy", 0)
                .style("fill", function() {
                    return color(data.id);
                })
                .text(data.type);
        },

        addYAxis: function() {},

        handleData: function(svg, data) {
            var that = this;

            var files = d3.keys(data)
                .sort()
                .map(function(file) {
                    return {
                        name: file,
                        metrics: d3.keys(data[file][0])
                            .sort()
                            .filter(function(key) {
                                return key !== "date";
                            })
                            .map(function(type) {
                                return {
                                    type: type,
                                    id: type.replace(" ", "_").toLowerCase(),
                                    values: data[file].map(function(d) {
                                        return {
                                            date: new Date(d.date),
                                            value: d[type]
                                        };
                                    })
                                };
                            })
                    };
                });

            var height = this.height + this.margins.bottom + this.margins.top;

            d3.select(".metrics svg")
                .attr("height", (files.length * height));

            files.forEach(function(file, index) {
                var offset = that.width / file.metrics.length;

                var color = d3.scale.category10();
                color.domain(d3.map(file.metrics, function(d) {
                    return d.id;
                }));

                var container = that.svg.append("g")
                    .attr("class", "file")
                    .attr("transform", "translate(0," + (index * height) + ")");

                file.metrics.forEach(function(metric, index) {
                    that.createMetric(container, metric, color, index * offset);
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
