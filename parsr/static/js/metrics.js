var Metrics;

(function() {

    Metrics = Graph.extend({

        init: function(target, attrs) {
            this.scales = {};

            this._super("metrics", target, attrs);
        },

        updateScale: function(svg, metrics) {
            var that = this;

            $.each(metrics, function() {
                var y = that.setScale(this, d3.scale.linear().range([that.height, 0]));

                svg.select(".axis-" + this.id)
                    .call(d3.svg.axis().scale(y).orient("left"));
            });
        },

        addYAxis: function() {},

        createSelect: function(files) {
            var select = $("<select />");

            $.each(files, function() {
                select.append(
                    "<option value='" + this.name + "'>" + this.name + "</option>"
                );
            });

            return select;
        },

        parse: function(data) {
            return d3.keys(data)
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
                                            id: type.replace(" ", "_").toLowerCase(),
                                            date: new Date(d.date),
                                            value: d[type]
                                        };
                                    })
                                };
                            })
                    };
                });
        },

        setScale: function(metric, scale) {
            this.scales[metric.id] = scale;

            scale.domain([
                d3.min(metric.values, function(d) {
                    return d.value;
                }),
                d3.max(metric.values, function(d) {
                    return d.value;
                })
            ]);

            return scale;
        },

        getScale: function(metric) {
            return this.scales[metric.id];
        },

        prepareDiagram: function(data) {
            var that = this;

            var color = d3.scale.category10();
            color.domain($.map(data, function(d) {
                return d.id;
            }));

            this.createAxis(data, color);

            var metric = that.svg.selectAll(".metric")
                .data(data)
                .enter().append("g")
                .attr("class", "metric");

            var line = d3.svg.line()
                .interpolate("basis")
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y(function(d) {
                    return that.getScale(d)(d.value);
                });

            metric.append("path")
                .attr("class", "line")
                .attr("d", function(d) {
                    return line(d.values);
                })
                .style("stroke", function(d) {
                    return color(d.id);
                });

            this.on("file.change", function(file) {
                that.svg.selectAll(".line")
                    .data(file.metrics)
                    .transition()
                    .attr("d", function(d) {
                        return line(d.values);
                    });
            });

            that.updateScale(that.svg, data);
        },

        createAxis: function(data, color) {
            var that = this;

            var offset = that.width / data.length;

            $.each(data, function(index) {
                that.setScale(this, d3.scale.linear().range([that.height, 0]));

                var metric = this;

                that.svg.append("g")
                    .attr("class", "y axis axis-" + this.id)
                    .attr("transform", "translate(" + (offset * index) + ", 0)");

                that.svg.append("text")
                    .attr("class", "header")
                    .attr("dx", offset * index)
                    .attr("dy", 0)
                    .style("fill", function() {
                        return color(metric.id);
                    })
                    .text(this.type);
            });
        },

        handleData: function(svg, data) {
            var that = this;

            var files = this.parse(data);

            this.prepareDiagram(files[0].metrics);

            var select = this.createSelect(files);

            this.dom.append(select);

            var getFile = function(name) {
                var result;

                $.each(files, function() {
                    if(this.name !== name) {
                        return;
                    }

                    result = this;
                });

                return result;
            };

            select.change(function() {
                var file = getFile(this.value);

                that.updateScale(that.svg, file.metrics);

                that.scale.x = d3.time.scale().range([0, that.width]);
                that.scale.x.domain(d3.extent(file.metrics[0].values, function(d) {
                    return d.date;
                }));

                that.svg.select(".x.axis")
                    .call(d3.svg.axis().scale(that.scale.x).orient("bottom"));

                that.raise("file.change", file);
            });
        }
    });

    Metrics.auto = function(target, attrs) {
        $(target || ".metrics").each(function() {
            new Metrics(this, attrs);
        });
    };

}());
