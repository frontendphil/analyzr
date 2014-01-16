ns("plugins.graph.metrics");

(function() {

    analyzr.plugins.graph.metrics.MetricsBase = analyzr.plugins.graph.Graph.extend({

        init: function(target, attrs) {
            this.scales = {};

            this.brushHeight = attrs.brushHeight || 50;
            this.brushMargin = attrs.brushMargin || 20;

            this._super("metrics", target, attrs);

            this.addStaticContent();
        },

        updateScale: function(svg, metrics, info) {
            var that = this;

            var first = true;
            var extent;

            if(!info) {
                extent = d3.extent(metrics[0] ? metrics[0].values : [], function(d) {
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
                var y = that.setScale(this, d3.scale.linear().range([that.getInnerHeight(), 0]));

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

        getBrush: function(clb) {
            var that = this;

            this.brush = d3.svg.brush()
                .x(this.scale.x2)
                .on("brush", function() {
                    that.handleBrush(clb);
                });

            return this.brush;
        },

        handleBrush: function(clb) {
            clb = clb || function() {};

            var domain = this.brush.empty() ? this.scale.x2.domain() : this.brush.extent();

            this.updateXAxis(domain[0], domain[1]);

            this.scale.x.domain(domain);

            clb();
        },

        prepareScale: function() {
            var scale = this._super();

            this.scale.x2 = d3.time.scale().range([0, this.getInnerWidth()]);

            return scale;
        },

        prepareAxis: function(x, y) {
            this._super(x, y);

            this.axis.x2 = d3.svg.axis().scale(this.scale.x2).orient("bottom").tickSize(-1 * this.getInnerHeight());
        },

        prepareSVG: function() {
            var svg = this._super();

            var y = this.getInnerHeight() + this.margins.top + this.brushMargin;

            var el = d3.select(this.dom.get(0)).select("svg");

            el.append("clipPath")
                .attr("id", "clip")
                .append("rect")
                    .attr("height", this.getInnerHeight())
                    .attr("width", this.getInnerWidth());

            var context = el.append("g")
                .attr("class", "filter")
                .attr("transform", "translate(" + this.margins.left + "," + y + ")");

            context.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.brushHeight + ")")
                .call(this.axis.x2);

            context.append("g")
                .attr("class", "x brush")
                .call(this.getBrush())
                .selectAll("rect")
                    .attr("y", -6)
                    .attr("height", this.brushHeight + 7);

            this.context = context;

            return svg;
        },

        addYAxis: function() {},

        getDiagramHeight: function() {
            return this._super() + this.brushHeight + this.brushMargin;
        },

        parse: function(data, kind) {
            return d3.keys(data)
                .map(function(file) {
                    var deleted = false;

                    var metrics = [];

                    if(data[file][0]) {
                        metrics = d3.keys(data[file][0].rep[kind])
                            .sort()
                            .filter(function(key) {
                                return !key.endsWith("_delta");
                            })
                            .map(function(type) {
                                return {
                                    type: type.capitalize(),
                                    id: type,
                                    values: data[file].map(function(d) {
                                        deleted = deleted || d.rep.deleted;

                                        return {
                                            id: type,
                                            date: new Date(d.rep.date),
                                            revision: d.rep.revision,
                                            value: d.rep[kind][type]
                                        };
                                    })
                                };
                            });
                    }

                    return {
                        name: file,
                        deleted: deleted,
                        metrics: metrics,
                        count: metrics[0] ? metrics[0].values.length : 0
                    };
                })
                .sort(function(a, b) {
                    return b.count - a.count;
                });
        },

        setScale: function(metric, scale) {
            this.scales[metric.id] = scale;
            this.scales[metric.id + "-brush"] = d3.scale.linear().range([this.brushHeight, 0]);

            var max = d3.max(metric.values, function(d) {
                return d.value;
            });

            var min = d3.min(metric.values, function(d) {
                return d.value;
            });

            min = Math.min(0, min);

            scale.domain([min, max]);

            this.scales[metric.id + "-brush"].domain(scale.domain());

            return scale;
        },

        getScale: function(metric) {
            return this.scales[metric.id];
        },

        getBrushScale: function(metric) {
            return this.scales[metric.id + "-brush"];
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

        updateXScale: function(svg, info) {
            this._super(svg, info);

            var domain = this.scale.x.domain();

            var x2 = d3.time.scale().range([0, this.getInnerWidth()]);
            x2.domain(domain);

            this.scale.x2 = x2;

            var axis = d3.svg.axis()
                .scale(x2)
                .orient("bottom")
                .tickSize(-1 * this.brushHeight);

            this.context.select(".x.axis")
                .call(axis);
        },

        createBrush: function(data, info, color) {
            var metric = this.context.selectAll(".metric")
                .data(data)
                .enter().append("g")
                .attr("class", "metric");

            var that = this;

            var line = d3.svg.line()
                .x(function(d) {
                    return that.scale.x2(d.date);
                })
                .y(function(d) {
                    return that.getBrushScale(d)(d.value);
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
                updateBrush(file.metrics);

                that.context.selectAll(".line")
                    .data(file.metrics)
                    .transition()
                    .attr("d", function(d) {
                        return line(d.values);
                    });
            });

            var updateBrush = function(data) {
                var brush = that.getBrush(function() {
                    var line = d3.svg.line()
                        .x(function(d) {
                            return that.scale.x(d.date);
                        })
                        .y(function(d) {
                            return that.getScale(d)(d.value);
                        });

                    that.svg.selectAll(".line")
                        .data(data)
                        .attr("d", function(d) {
                            return line(d.values);
                        });
                });

                that.context.select(".brush").call(brush);
            };

            updateBrush(data);
        },

        prepareDiagram: function(data, info) {
            var that = this;

            var color = d3.scale.category10();
            color.domain($.map(data, function(d) {
                return d.id;
            }));

            this.createAxis(data, info, color);
            this.createBrush(data, info, color);

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
                    var stepSize = that.getInnerWidth() / data.length;
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
                .attr("clip-path", "url(#clip)")
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

            // remove old background
            this.svg.select(".background").remove();

            this.svg.append("rect")
                .attr("class", "background")
                .attr("width", this.getInnerWidth())
                .attr("height", this.getInnerHeight());
        },

        createAxis: function(data, info, color) {
            var that = this;

            $.each(data, function(index) {
                that.setScale(this, d3.scale.linear().range([that.getInnerHeight(), 0]));

                var metric = this;

                var xOffset = index % 2 === 0 ? 0 : (that.getInnerWidth() - 5);
                xOffset = xOffset + (index % 2 === 0 ? -1 : 1) * index * 20;

                // remove old axis
                that.svg.selectAll(".axis-" + this.id).remove();
                that.svg.selectAll(".header-" + this.id).remove();

                that.svg.append("g")
                    .attr("class", "y axis axis-" + this.id)
                    .attr("transform", "translate(" + xOffset + ", 0)");

                that.svg.append("text")
                    .attr("class", "header header-" + this.id)
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

        getXY: function(metric, date) {
            if(!metric) {
                return;
            }

            var value = this.nearestValue($.map(metric.values, function(value) {
                return value.date;
            }), date);

            var x = value;
            var y;
            var revision;

            $.each(metric.values, function() {
                if(this.date.toISOString() !== value.toISOString()) {
                    return;
                }

                y = this.value;
                revision = this.revision;
            });

            return {
                x: x,
                y: y,
                revision: revision
            };
        },

        handleClick: function(args, file) {
            var mouse = d3.mouse(args);

            var x = mouse[0];

            var domain = this.scale.x.domain();

            var date = this.scale.x.invert(x);
            date = this.constrain(date, domain[0], domain[1]);

            var nearest = this.getXY(file.metrics[0], date);

            if(!nearest) {
                // empty screen
                return;
            }

            var pkg = this.filter.getCurrentPackage();
            var file = this.filter.getCurrentFile();

            var info = new analyzr.plugins.RevisionInfo(nearest.revision);
            info.show(pkg, file);
        },

        handleMouseMove: function(args, metrics) {
            var mouse = d3.mouse(args);

            var x = mouse[0];
            var y = mouse[1];

            var date = this.scale.x.invert(x);
            date = this.constrain(date, this.scale.x.domain()[0], this.scale.x.domain()[1]);

            var that = this;

            var moveCircles = function(metric, scale, isLine) {
                return function(selection) {
                    return selection.attr("transform", function() {
                        var coord = that.getXY(metric, date);

                        var x = that.scale.x(coord.x);
                        var y = isLine ? 0 : scale(coord.y);

                        return "translate(" + x + "," + y + ")";
                    });
                };
            };

            var updateValue = function(metric) {
                return function(selection) {
                    return selection.text(function() {
                        var coord = that.getXY(metric, date);

                        return Math.round(coord.y, 2);
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

        createDataPreview: function(file) {
            var that = this;

            this.svg.select(".background")
                .on("mousemove", function() {
                    that.handleMouseMove(this, file.metrics);
                })
                .on("click", function() {
                    that.handleClick(this, file);
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
            if(!value) {
                return;
            }

            var file = this.getFile(value);

            this.updateScale(this.svg, file.metrics);
            this.createDataPreview(file);

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
                .attr("y1", this.getInnerHeight())
                .style("stroke", "#000");
        },

        getKind: function() {},

        handleData: function(svg, response) {
            var that = this;

            this.files = this.parse(response.data, this.getKind());

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
