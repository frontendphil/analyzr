var Graph;

(function() {

    Graph = Component.extend({

        init: function(base, target, attrs) {
            attrs = attrs || {};

            this.margins = this.createMargins(attrs.margins || {});

            this.width = (attrs.width || $(target).width()) - this.margins.left - this.margins.right;
            this.height = (attrs.height || 400) - this.margins.top - this.margins.bottom;

            this.dom = $(target);
            this.svg = this.prepareSVG();
            this.addAxis(this.svg);

            this._super(base, target);

            var that = this;

            this.filter = new Filter(this.dom, function() {
                that.setup(that.url + "?" + this.toQueryString(), that.branch);
            });

            this.filter.on("file.selected", function(value) {
                that.handleFileSelect(value);
            });
        },

        handleFileSelect: function() {},

        getTickValues: function(start, end) {
            var span = start.to(end);

            if(span.years > 0) {
                return d3.time.months(start, end, span.years);
            }

            if(span.months > 0) {
                return d3.time.weeks(start, end, span.months);
            }

            if(span.weeks > 0) {
                return d3.time.days(start, end, span.weeks);
            }

            if(span.days > 0) {
                return d3.time.hours(start, end, Math.floor(span.hours / 2));
            }

            if(span.hours > 0) {
                return d3.time.minutes(start, end, span.hours);
            }

            return d3.time.minutes(start, end, 1);
        },

        updateXScale: function(svg, info) {
            var start = info.options.startDate || info.options.minDate;
            var end = info.options.endDate || info.options.maxDate;

            var x = d3.time.scale().range([0, this.width]);
            x.domain([start, end]);

            this.scale.x = x;

            var axis = d3.svg.axis()
                .scale(x)
                .orient("bottom")
                .tickValues(this.getTickValues(start, end))
                .tickSize(-this.getInnerHeight());

            this.axis.x = axis;

            svg.select(".x.axis")
                .call(axis);
        },

        updateYScale: function(svg, info) {
            var y = d3.scale.linear().range([this.height, 0]);
            y.domain([info.options.lowerBound, info.options.upperBound]);

            this.scale.y = y;

            var axis = d3.svg.axis()
                .scale(y)
                .orient("left")
                .tickSize(-this.getInnerWidth());

            this.axis.y = axis;

            svg.select(".y.axis")
                .call(axis);
        },

        updateScales: function(svg, info) {
            this.updateXScale(svg, info);
            this.updateYScale(svg, info);
        },

        createMargins: function(margins) {
            return {
                top: margins.top || 0,
                left: margins.left || 0,
                bottom: margins.bottom || 0,
                right: margins.right || 0
            };
        },

        updateFilters: function(info, files) {
            this.filter.update({
                files: files,
                languages: info.languages,
                langauge: info.options.language,
                startDate: info.options.startDate || info.options.minDate,
                endDate: info.options.endDate || info.options.maxDate
            });
        },

        getInnerWidth: function() {
            return this.width;
        },

        getInnerHeight: function() {
            return this.height;
        },

        prepareScale: function() {
            this.scale = {
                x: d3.time.scale().range([0, this.width]),
                y: d3.scale.linear().range([this.height, 0])
            };

            return this.scale;
        },

        prepareAxis: function(x, y) {
            this.axis = {
                x: d3.svg.axis().scale(x).orient("bottom").tickSize(-1 * this.getInnerHeight()),
                y: d3.svg.axis().scale(y).orient("left").tickSize(-1 * this.getInnerWidth())
            };
        },

        prepareSVG: function() {
            var scale = this.prepareScale();
            this.prepareAxis(scale.x, scale.y);

            return d3.select(this.dom.get(0)).append("svg")
                .attr("class", "chart")
                .attr("width", this.width + this.margins.left + this.margins.right)
                .attr("height", this.height + this.margins.top + this.margins.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margins.left + "," + this.margins.top + ")");
        },

        createDomain: function(data, min, max) {
            this.scale.x.domain(d3.extent(data.info.dates));

            this.scale.y.domain([
                d3.min(data.data, min),
                d3.max(data.data, max)
            ]);

            var domain = this.scale.x.domain();

            this.axis.x.ticks(d3.time.days(domain[0], domain[1]).length);
        },

        addAxis: function(svg) {
            this.addXAxis(svg);
            this.addYAxis(svg);
        },

        addXAxis: function(svg) {
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.height + ")")
                .call(this.axis.x)
                .selectAll("text")
                    .style("text-anchor", "end")
                    .attr("transform", "rotate(-65)");
        },

        addYAxis: function(svg) {
            svg.append("g")
                .attr("class", "y axis")
                .call(this.axis.y);
        },

        beforeRequest: function() {},

        getMinValue: function(d) {
            return d.value;
        },

        getMaxValue: function(d) {
            return d.value;
        },

        parseInfos: function(info) {
            if(info.options.startDate) {
                info.options.startDate = new Date(info.options.startDate);
            }

            if(info.options.endDate) {
                info.options.endDate = new Date(info.options.endDate);
            }

            if(info.options.minDate) {
                info.options.minDate = new Date(info.options.minDate);
            }

            if(info.options.maxDate) {
                info.options.maxDate = new Date(info.options.maxDate);
            }

            info.dates = info.dates.map(function(date) {
                return new Date(date);
            });
        },

        setup: function(url) {
            this.beforeRequest();

            var that = this;

            this.mask("Loading graph data...");

            d3.json(url, function(response) {
                that.unmask();
                that.parseInfos(response.info);
                that.createDomain(response, that.getMinValue, that.getMaxValue);
                that.handleData(that.svg, response);
            });
        }

    });

}());
