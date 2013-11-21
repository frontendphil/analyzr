var Metrics;

(function() {

    Metrics = Graph.extend({

        init: function(target, attrs) {
            this.scales = {};

            this._super("metrics", target, attrs);
        },

        updateScale: function(svg, metrics) {
            var that = this;

            var first = true;

            $.each(metrics, function(index) {
                var y = that.setScale(this, d3.scale.linear().range([that.height, 0]));

                var axis = d3.svg.axis()
                    .scale(y)
                    .orient(index % 2 === 0 ? "left" : "right");

                if(first) {
                    first = false;

                    axis.tickSize(-1 * that.getInnerWidth(), -1 * that.getInnerWidth(), 5);
                }

                svg.select(".axis-" + this.id)
                    .call(axis);
            });

            that.createDataPreview(metrics);
        },

        addYAxis: function() {},

        createSelect: function(files) {
            var select = $("<select />");

            $.each(files, function() {
                var deleted = "";

                if(this.deleted) {
                    deleted = " - DELETED";
                }

                select.append(
                    "<option value='" + this.name + "'>" +
                        this.name + " (" + this.count + ")" + deleted +
                    "</option>"
                );
            });

            return select;
        },

        parse: function(data) {
            return d3.keys(data)
                .map(function(file) {
                    var deleted = false;

                    var metrics = d3.keys(data[file][0])
                        .sort()
                        .filter(function(key) {
                            return key !== "date" && key !== "deleted";
                        })
                        .map(function(type) {
                            return {
                                type: type,
                                id: type.replace(" ", "_").toLowerCase(),
                                values: data[file].map(function(d) {
                                    deleted = deleted || d.deleted;

                                    return {
                                        id: type.replace(" ", "_").toLowerCase(),
                                        date: new Date(d.date),
                                        value: d[type]
                                    };
                                })
                            };
                        });

                    return {
                        name: file,
                        deleted: deleted,
                        metrics: metrics,
                        count: metrics[0].values.length
                    };
                })
                .sort(function(a, b) {
                    return b.count - a.count;
                });
        },

        setScale: function(metric, scale) {
            this.scales[metric.id] = scale;

            scale.domain([
                0,
                d3.max(metric.values, function(d) {
                    return d.value;
                })
            ]);

            return scale;
        },

        getScale: function(metric) {
            return this.scales[metric.id];
        },

        createCircle: function(parent, color) {
            parent.append("circle")
                .attr("class", "outer")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", 7)
                .style("fill", function(d) {
                    return color(d.id);
                });

            parent.append("circle")
                .attr("class", "ring")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", 5)
                .style("fill", "#fff");

            parent.append("circle")
                .attr("class", "center")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", 4)
                .style("fill", function(d) {
                    return color(d.id);
                });

            parent.append("text")
                .attr("class", "text")
                .attr("dx", 10)
                .attr("dy", 5)
                .append("tspan")
                    .attr("class", "value")
                    .style("fill", function(d) {
                        return color(d.id);
                    });
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

            var circle = that.svg.selectAll(".circle")
                .data(data)
                .enter().append("g")
                .attr("class", function(d) {
                    return "circle circle-" + d.id;
                });

            this.createCircle(circle, color);

            var line = d3.svg.line()
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

            this.svg.append("rect")
                .attr("class", "background")
                .attr("width", this.width)
                .attr("height", this.height);
        },

        createAxis: function(data, color) {
            var that = this;

            $.each(data, function(index) {
                that.setScale(this, d3.scale.linear().range([that.height, 0]));

                var metric = this;

                var xOffset = index % 2 === 0 ? 0 : (that.width - 5);
                xOffset = xOffset + (index % 2 === 0 ? -1 : 1) * index * 25;

                that.svg.append("g")
                    .attr("class", "y axis axis-" + this.id)
                    .attr("transform", "translate(" + xOffset + ", 0)");

                that.svg.append("text")
                    .attr("class", "header")
                    .attr("dx", 0)
                    .attr("dy", index % 2 === 0 ? xOffset + 15 : xOffset - 5)
                    .attr("transform", "rotate(-90)")
                    .style("text-anchor", "end")
                    .style("fill", function() {
                        return color(metric.id);
                    })
                    .text(this.type);
            });
        },

        handleMouseEnter: function() {
            this.svg.selectAll(".circle")
                .transition()
                .attr("opacity", 1);
        },

        handleMouseLeave: function() {
            this.svg.selectAll(".circle")
                .transition()
                .attr("opacity", 0);
        },

        constrain: function(value, min, max) {
            if(value < min) {
                return min;
            }

            if(value > max) {
                return max;
            }

            return value;
        },

        nearestValue: function(space, needle) {
            var result = space[0];

            $.each(space, function() {
                if(this <= needle) {
                    result = this;
                }
            });

            return result;
        },

        handleMouseMove: function(args, metrics) {
            var mouse = d3.mouse(args);

            var x = mouse[0];
            var y = mouse[1];

            var date = this.scale.x.invert(x);
            date = this.constrain(date, this.scale.x.domain()[0], this.scale.x.domain()[1]);

            var that = this;

            var getXY = function(metric) {
                var value = that.nearestValue($.map(metric.values, function(value) {
                    return value.date;
                }), date);

                var x = value;
                var y;

                $.each(metric.values, function() {
                    if(this.date.toISOString() !== value.toISOString()) {
                        return;
                    }

                    y = this.value;
                });

                return {
                    x: x,
                    y: y
                };
            };

            var moveCircles = function(metric, scale) {
                return function(selection) {
                    return selection.attr("transform", function() {
                        var coord = getXY(metric, scale);

                        return "translate(" + that.scale.x(coord.x) + "," + scale(coord.y) + ")";
                    });
                };
            };

            var updateValue = function(metric, scale) {
                return function(selection) {
                    return selection.text(function() {
                        var coord = getXY(metric, scale);

                        return coord.y;
                    });
                };
            };

            $.each(metrics, function() {
                var scale = that.getScale(this);

                if(y > scale.range()[0]) {
                    that.handleMouseLeave();

                    return;
                }

                that.svg.selectAll(".circle-" + this.id).call(moveCircles(this, scale));
                that.svg.selectAll(".circle-" + this.id + " .value").call(updateValue(this, scale));
            });
        },

        createDataPreview: function(metrics) {
            var that = this;

            this.svg.select(".background").on("mousemove", function() {
                that.handleMouseMove(this, metrics);
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

            this.svg.select(".background")
                .on("mouseenter", function() {
                    that.handleMouseEnter();
                })
                .on("mouseleave", function() {
                    that.handleMouseLeave();
                });

            this.handleMouseLeave();

            select.change(function() {
                var file = getFile(this.value);

                that.updateScale(that.svg, file.metrics);

                that.scale.x = d3.time.scale().range([0, that.width]);
                that.scale.x.domain(d3.extent(file.metrics[0].values, function(d) {
                    return d.date;
                }));

                var domain = that.scale.x.domain();

                var axis = d3.svg.axis()
                    .scale(that.scale.x)
                    .orient("bottom")
                    .ticks(d3.time.days(domain[0], domain[1]).length)
                    .tickSize(-that.getInnerHeight());

                that.svg.select(".x.axis")
                    .call(axis)
                    .selectAll("text")
                        .style("text-anchor", "end")
                        .attr("transform", "rotate(-65)");

                that.raise("file.change", file);
            });

            select.change();
        }
    });
}());
