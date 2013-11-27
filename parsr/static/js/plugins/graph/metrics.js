var Metrics;

(function() {

    Metrics = Graph.extend({

        init: function(target, attrs) {
            this.scales = {};
            this.params = {};

            this._super("metrics", target, attrs);

            var that = this;

            this.dom.find(".update-filters").click(function() {
                var params = [];

                $.each(that.params, function(key, value) {
                    params.push(key + "=" + value);
                });

                that.setup(that.url + "?" + params.join("&"), that.branch);

                return false;
            });

            this.on("file.selected", function(value) {
                that.handleFileSelect(value);
            });
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

        createSelect: function(kind, values, clb) {
            var cls = "filter-" + kind.replace(" ", "-").toLowerCase();

            var container = this.dom.find("." + cls);
            var select = container.find("select");

            if(container.length === 0) {
                container = $("<div class='input-group col-lg-1 col-md-3 " + cls + "' />");
                select = $(
                    "<select class='form-control'>" +
                        "<option value=''>" + kind.capitalize() + "</option>" +
                        "<option value=''>----</option>" +
                        "<option value='all'>All</option>" +
                    "</select>"
                );

                container.append(select);
            }

            select.find("option").each(function() {
                var option = $(this);
                var value = option.attr("value");

                if(value && value !== "all") {
                    option.remove();
                }
            });

            $.each(values, function() {
                var item = clb(this);

                if(!item) {
                    return;
                }

                select.append(
                    "<option value='" + item.value + "'>" +
                        item.text +
                    "</option>"
                );
            });

            container.val = function() {
                select.val.apply(select, arguments);
            };

            container.change = function() {
                select.change.apply(select, arguments);
            };

            return container;
        },

        createFileSelector: function(files) {
            var select = this.createSelect("file", files, function(file) {
                var deleted = "";

                if(file.deleted) {
                    deleted = " - DELETED";
                }

                return {
                    value: file.name,
                    text: file.name + " (" + file.count + ")" + deleted
                };
            });

            if(files.length === 0) {
                select.remove();

                return;
            }

            var that = this;

            select.change(function() {
                that.raise("file.selected", this.value);
            });

            return select;
        },

        createLanguageSelector: function(languages, value) {
            var select = this.createSelect("language", languages, function(language) {
                return {
                    value: language.toString(),
                    text: language.toString()
                };
            });

            if(value) {
                select.val(value);
            }

            var that = this;

            select.change(function() {
                if(!this.value) {
                    return;
                }

                that.changeParam("language", this.value);
            });

            return select;
        },

        changeParam: function(key, value) {
            this.params[key] = value;
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

        formatDate: function(date) {
            return date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getUTCFullYear();
        },

        createDatePicker: function(info) {
            var that = this;
            var options = info.options;

            var createPicker = function(element, value, clb) {
                var date = that.formatDate(new Date(value));

                element.find("input").val(date);

                var button = element.find(".input-group-addon");
                button.data("date", date);
                button.datepicker({
                    format: "dd/mm/yyyy",
                    viewMode: "years"
                });
                button.on("changeDate", function(event) {
                    if(event.viewMode !== "days") {
                        return;
                    }

                    element.find("input").val(that.formatDate(event.date));

                    clb(event.date);
                });

                that.changeParam(element.data("rel"), date);
            };

            createPicker($(".date-from"), options.startDate || options.minDate, function(date) {
                that.changeParam("from", date.toISOString());
            });
            createPicker($(".date-to"), options.endDate || options.maxDate, function(date) {
                that.changeParam("to", date.toISOString());
            });
        },

        addFilters: function(files, info) {
            this.createDatePicker(info);

            var fileSelector = this.createFileSelector(files);
            var languageSelector = this.createLanguageSelector(info.languages, info.options.language);

            this.dom.find(".filters").append(languageSelector, fileSelector);
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

            this.scale.x = d3.time.scale().range([0, this.width]);
            this.scale.x.domain(d3.extent(file.metrics[0].values, function(d) {
                return d.date;
            }));

            var domain = this.scale.x.domain();

            var axis = d3.svg.axis()
                .scale(this.scale.x)
                .orient("bottom")
                .ticks(d3.time.days(domain[0], domain[1]).length)
                .tickSize(-this.getInnerHeight());

            this.svg.select(".x.axis")
                .call(axis)
                .selectAll("text")
                    .style("text-anchor", "end")
                    .attr("transform", "rotate(-65)");

            this.raise("file.change", file);
        },

        handleData: function(svg, response) {
            var that = this;

            this.files = this.parse(response.data);
            var metrics = [];

            this.addFilters(this.files, response.info);

            if(this.files.length > 0) {
                metrics = this.files[0].metrics;
            }

            this.svg.append("line")
                .attr("class", "position")
                .attr("opacity", 0.2)
                .attr("x0", 0)
                .attr("x1", 0)
                .attr("y0", 0)
                .attr("y1", this.height)
                .style("stroke", "#000");

            this.prepareDiagram(metrics);

            this.svg.select(".background")
                .on("mouseenter", function() {
                    that.handleMouseEnter();
                })
                .on("mouseleave", function() {
                    that.handleMouseLeave();
                });

            this.handleMouseLeave();
        }
    });
}());
