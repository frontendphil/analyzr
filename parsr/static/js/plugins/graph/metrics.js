var Metrics;

(function() {

    Metrics = Graph.extend({

        init: function(target, attrs) {
            this.scales = {};

            this._super("metrics", target, attrs);

            this.addStaticContent();
        },

        updateScale: function(svg, metrics, info) {
            var that = this;

            var first = true;
            var extent;

            if(!info) {
                extent = d3.extent(metrics[0].values, function(d) {
                    return d.date;
                });
            } else {
                extent = [info.options.startDate, info.options.endDate];
            }

            this.updateXScale(svg, info || {
                options: {
                    startDate: extent[0],
                    endDate: extent[1]
                }
            });

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
        },

        addYAxis: function() {},

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

        createComplexCircle: function(parent, color) {
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
        },

        createCircle: function(parent, value, color) {
            this.createComplexCircle(parent, color);
            this.createComplexCircle(value, color);

            value.append("text")
                .attr("dx", 10)
                .attr("dy", 5)
                .style("fill", function(d) {
                    return color(d.id);
                });
        },

        prepareDiagram: function(data, info) {
            var that = this;

            var color = d3.scale.category10();
            color.domain($.map(data, function(d) {
                return d.id;
            }));

            this.createAxis(data, info, color);

            var metric = that.svg.selectAll(".metric")
                .data(data)
                .enter().append("g")
                .attr("class", "metric");

            var circle = that.svg.selectAll(".circle")
                .data(data)
                .enter().append("g")
                .attr("class", function(d) {
                    return "optional circle circle-" + d.id;
                });

            var text = this.svg.selectAll(".value")
                .data(data)
                .enter().append("g")
                .attr("class", function(d) {
                    return "optional value value-" + d.id;
                })
                .attr("transform", function(d, index) {
                    var stepSize = that.width / data.length;
                    var offset = stepSize / 2;

                    return "translate(" + ((index * stepSize) + offset) + ",-" + (that.margins.top / 2) + ")";
                });

            this.createCircle(circle, text, color);

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

            this.on("file.changed", function(file) {
                that.svg.selectAll(".line")
                    .data(file.metrics)
                    .transition()
                    .attr("d", function(d) {
                        return line(d.values);
                    });
            });

            that.updateScale(that.svg, data, info);

            // remove old background
            this.svg.select(".background").remove();

            this.svg.append("rect")
                .attr("class", "background")
                .attr("width", this.width)
                .attr("height", this.height);
        },

        createAxis: function(data, info, color) {
            var that = this;

            $.each(data, function(index) {
                that.setScale(this, d3.scale.linear().range([that.height, 0]));

                var metric = this;

                var xOffset = index % 2 === 0 ? 0 : (that.width - 5);
                xOffset = xOffset + (index % 2 === 0 ? -1 : 1) * index * 25;

                // remove old axis
                that.svg.selectAll(".axis-" + this.id).remove();

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
            this.svg.selectAll(".optional")
                .transition()
                .attr("opacity", 1);

            this.svg.selectAll(".position")
                .transition()
                .attr("opacity", 0.2);
        },

        handleMouseLeave: function() {
            this.svg.selectAll(".optional")
                .transition()
                .attr("opacity", 0);

            this.svg.selectAll(".position")
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

            var moveCircles = function(metric, scale, isLine) {
                return function(selection) {
                    return selection.attr("transform", function() {
                        var coord = getXY(metric, scale);

                        var x = that.scale.x(coord.x);
                        var y = isLine ? 0 : scale(coord.y);

                        return "translate(" + x + "," + y + ")";
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

                that.handleMouseEnter();

                that.svg.selectAll(".circle-" + this.id).call(moveCircles(this, scale));
                that.svg.selectAll(".position").call(moveCircles(this, scale, true));
                that.svg.selectAll(".value-" + this.id + " text").call(updateValue(this, scale));
            });
        },

        createDataPreview: function(metrics) {
            var that = this;

            this.svg.select(".background").on("mousemove", function() {
                that.handleMouseMove(this, metrics);
            });
        },

        getFile: function(name) {
            var result;

            $.each(this.files, function() {
                if(result || this.name !== name) {
                    return;
                }

                result = this;
            });

            return result;
        },

        handleFileSelect: function(value) {
            if(!value || value === "all") {
                return;
            }

            var file = this.getFile(value);

            this.updateScale(this.svg, file.metrics);
            this.createDataPreview(file.metrics);

            this.raise("file.changed", file);
        },

        addStaticContent: function() {
            this.svg.select(".position").remove();
            this.svg.append("line")
                .attr("class", "position")
                .attr("opacity", 0)
                .attr("x0", 0)
                .attr("x1", 0)
                .attr("y0", 0)
                .attr("y1", this.height)
                .style("stroke", "#000");
        },

        handleData: function(svg, response) {
            var that = this;

            this.updateXScale(this.svg, response.info);

            this.files = this.parse(response.data);

            if(this.files.length === 0) {
                this.updateFilters(response.info, this.files);

                return;
            }

            var metrics = this.files[0].metrics;

            this.prepareDiagram(metrics, response.info);

            this.svg.selectAll(".background")
                .on("mouseenter", function() {
                    that.handleMouseEnter();
                })
                .on("mouseleave", function() {
                    that.handleMouseLeave();
                });

            this.handleMouseLeave();
            this.updateFilters(response.info, this.files);
        }
    });
}());
