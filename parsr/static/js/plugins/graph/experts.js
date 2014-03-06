ns("plugins.graph");

(function() {

    analyzr.plugins.graph.Experts = analyzr.plugins.graph.Graph.extend({

        init: function(target, attrs) {
            attrs.title = "Code Experts";

            this._super("experts", target, attrs);

            var title = this.dom.find(".graph-title.hidden-print");
            title.append("<small><a href='" + this.branch + "/experts/detail'>I want more details!</a></small>");
        },

        createDomain: function(svg, data, info) {
            this.updateXScale(svg, info);

            this.scale.y.domain([0, d3.max(d3.keys(data), function(key) {
                return data[key].score;
            })]);
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
                        start: entry.date,
                        values: [{
                            date: entry.date,
                            score: entry.value.score
                        }]
                    };

                    return;
                }

                if(current.author === entry.value.href) {
                    current.values.push({
                        date: entry.date,
                        score: entry.value.score
                    });

                    return;
                }

                if(!authors[current.author]) {
                    authors[current.author] = {
                        href: current.author,
                        ranges: [],
                        values: []
                    };
                }

                authors[current.author].ranges.push([current.start, entry.date]);
                authors[current.author].values.push(current.values);

                current = {
                    author: entry.value.href,
                    start: entry.date,
                    values: [{
                        date: entry.date,
                        score: entry.value.score
                    }]
                };
            });

            if(current && !authors[current.author]) {
                authors[current.author] = {
                    href: current.author,
                    ranges: [
                        [current.start, info.options.maxDate]
                    ],
                    values: [current.values]
                };
            }

            var ranges = [];

            d3.keys(authors).map(function(key) {
                var author = authors[key];

                author.ranges.forEach(function(range) {
                    ranges.push({
                        author: author.href,
                        scores: author.scores,
                        range: range
                    });
                });
            });

            return {
                ranges: ranges,
                authors: authors
            };
        },

        getAuthor: function(element) {
            var classes = $(element).attr("class");
            return classes.split(" ")[1];
        },

        allInstances: function(element) {
            var author = this.getAuthor(element);

            return d3.selectAll("." + author);
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
            var that = this;

            this.allInstances(element).attr("fill", fill.darker(0.6));

            $(element).data("fill", color(author));

            $(element).qtip({
                content: {
                    text: function(event, api) {
                        analyzr.core.data.get(author + "?branch=" + that.dom.data("branch"), {
                            success: function(data) {
                                api.set("content.text", data.rep.name);
                            }
                        });

                        return "Loading...";
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
            this.allInstances(element).attr("fill", $(element).data("fill"));
        },

        prepareDiagram: function(svg, data) {
            var that = this;

            var colors = d3.scale.category20c();
            colors.domain(d3.keys(data.authors));

            svg.selectAll(".y.axis")
                .call(this.axis.y);

            svg.selectAll(".author").remove();

            $.each(data.authors, function() {
                var author = this.href;

                var fill = colors(author);
                var stroke = d3.rgb(fill).darker(0.5);

                $.each(this.values, function() {
                    var area = svg.append("path")
                        .attr("class", "author href" + author.replace(/\//g, "-"));

                    var edge = svg.append("path")
                        .attr("class", "author edge");

                    var line = d3.svg.line()
                        .x(function(d) {
                            return that.scale.x(d.date);
                        })
                        .y(function(d) {
                            return that.scale.y(d.score);
                        });

                    var score = d3.svg.area()
                        .x(function(d) {
                            return that.scale.x(d.date);
                        })
                        .y1(function(d) {
                            return that.scale.y(d.score);
                        })
                        .y0(function() {
                            return that.scale.y(0);
                        });

                    area.datum(this)
                        .attr("d", score)
                        .attr("fill", fill);

                    edge.datum(this)
                        .attr("d", line)
                        .attr("stroke", stroke);
                });
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
