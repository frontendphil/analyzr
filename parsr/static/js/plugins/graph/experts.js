ns("plugins.graph");

(function() {

    analyzr.plugins.graph.Experts = analyzr.plugins.graph.Graph.extend({

        init: function(target, attrs) {
            attrs.title = "Code Experts";

            this._super("experts", target, attrs);
        },

        createDomain: function(svg, data, info) {
            this.updateXScale(svg, info);

            this.scale.y.domain(d3.extent(d3.keys(data), function(key) {
                return data[key].score;
            }));
        },

        parse: function(data, info) {
            var authors = {};
            var current;

            var values = d3.keys(data).map(function(key) {
                return {
                    date: new Date(key),
                    value: data[key]
                };
            }).sort(function(a, b) {
                return a.date - b.date;
            });

            values.forEach(function(entry) {
                if(!current) {
                    current = {
                        author: entry.value.href,
                        score: entry.value.score,
                        start: entry.date
                    };

                    return;
                }

                if(current.author === entry.value.href) {
                    current.score = Math.max(current.score, entry.value.score);

                    return;
                }

                if(!authors[current.author]) {
                    authors[current.author] = {
                        href: current.author,
                        score: current.score,
                        ranges: []
                    };
                }

                authors[current.author].ranges.push([current.start, entry.date]);

                current = {
                    author: entry.value.href,
                    score: entry.value.score,
                    start: entry.date
                };
            });

            if(current && !authors[current.author]) {
                authors[current.author] = {
                    href: current.author,
                    score: current.score,
                    ranges: [
                        [current.start, info.options.maxDate]
                    ]
                };
            }

            var ranges = [];

            d3.keys(authors).map(function(key) {
                var author = authors[key];

                author.ranges.forEach(function(range) {
                    ranges.push({
                        author: author.href,
                        score: author.score,
                        range: range
                    });
                });
            });

            return {
                ranges: ranges,
                authors: authors
            };
        },

        handleMouseEnter: function(element, data, color) {
            var mouse = d3.mouse(element);
            var x = mouse[0];

            var position = new Date(Math.floor(this.scale.x.invert(x)));
            var author;

            data.ranges.forEach(function(range) {
                if(author) {
                    return;
                }

                if(range.range[0] > position || position > range.range[1]) {
                    return;
                }

                author = range.author;
            });

            var fill = d3.rgb(color(author));

            d3.select(element).attr("fill", fill.darker(0.5));

            $(element).data("fill", color(author));

            $(element).qtip({
                content: {
                    text: "Loading...",
                    ajax: {
                        url: author + "?branch=" + this.dom.data("branch"),
                        type: "GET",
                        success: function(data) {
                            this.set("content.text", data.rep.name);
                        }
                    }
                },
                position: {
                    my: "bottom center",
                    at: "top center",
                    adjust: {
                        y: -10
                    }
                },
                style: {
                    classes: "qtip-dark qtip-tipsy qtip-shadow",
                    tip: "bottomMiddle"
                }
            });
        },

        handleMouseLeave: function(element) {
            d3.select(element).attr("fill", $(element).data("fill"));
        },

        prepareDiagram: function(svg, data, info) {
            var that = this;

            // this.createAxis(svg, data, info);

            var colors = d3.scale.category20c();
            colors.domain(d3.keys(data.authors));

            svg.selectAll(".y.axis")
                .call(this.axis.y);

            svg.selectAll(".author").remove();

            svg.selectAll(".author")
                .data(data.ranges)
                .enter().append("rect")
                .attr("class", "author")
                .attr("x", function(d) {
                    return that.scale.x(d.range[0]);
                })
                .attr("width", function(d) {
                    var start = that.scale.x(d.range[0]);
                    var end = that.scale.x(d.range[1]);

                    return end - start;
                })
                .attr("y", function(d) {
                    return that.scale.y(d.score);
                })
                .attr("height", function(d) {
                    return that.getInnerHeight() - that.scale.y(d.score);
                })
                .attr("fill", function(d) {
                    return colors(d.author);
                });

            svg.selectAll(".author")
                .on("mouseenter", function() {
                    that.handleMouseEnter(this, data, colors);
                })
                .on("mouseleave", function() {
                    that.handleMouseLeave(this);
                });
        },

        handleData: function(svg, response) {
            this.updateFilters(response.info);

            var data = this.parse(response.data, response.info);

            this.prepareDiagram(svg, data, response.info);
        }

    });

}());
