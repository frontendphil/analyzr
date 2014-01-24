ns("plugins.graph");

(function() {

    analyzr.plugins.graph.Graph = analyzr.core.Component.extend({

        init: function(base, target, attrs) {
            attrs = attrs || {};

            this.baseName = base;

            this.margins = this.createMargins(attrs.margins || {});

            this.width = (attrs.width || $(target).width()) - this.margins.left - this.margins.right;
            this.height = (attrs.height || 400) - this.margins.top - this.margins.bottom;

            this.dom = $(target);
            this.svg = this.prepareSVG();
            this.addAxis(this.svg);

            this._super(base, target, attrs.params);

            var that = this;

            if(attrs.noFilter) {
                return;
            }

            this.filter = new analyzr.plugins.Filter(this.dom, function() {
                that.setup(that.url + "?" + this.toQueryString(), that.branch);
            });

            this.filter.on("file.selected", function(value) {
                that.handleFileSelect(value);
            });
        },

        handleFileSelect: function() {},

        updateXAxis: function() {
            var axis = d3.svg.axis()
                .scale(this.scale.x)
                .orient("bottom")
                .tickSize(-this.getInnerHeight());

            this.axis.x = axis;

            this.svg.select(".x.axis")
                .call(axis);
        },

        updateXScale: function(svg, info) {
            var start = info.options.startDate || info.options.minDate;
            var end = info.options.endDate || info.options.maxDate;

            var x = d3.time.scale().range([0, this.getInnerWidth()]);
            x.domain([start, end]);

            this.scale.x = x;

            this.updateXAxis(start, end);
        },

        updateYScale: function(svg, info) {
            var y = d3.scale.linear().range([this.getInnerHeight(), 0]);
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
                language: info.options.language,
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
                x: d3.time.scale().range([0, this.getInnerWidth()]),
                y: d3.scale.linear().range([this.getInnerHeight(), 0])
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
                .attr("class", "canvas")
                .attr("width", this.getDiagramWidth())
                .attr("height", this.getDiagramHeight())
                .append("g")
                .attr("class", "chart chart-" + this.baseName)
                .attr("transform", "translate(" + this.margins.left + "," + this.margins.top + ")");
        },

        getDiagramHeight: function() {
            return this.height + this.margins.top + this.margins.bottom;
        },

        getDiagramWidth: function() {
            return this.width + this.margins.left + this.margins.right;
        },

        createDomain: function(svg, data, info) {
            this.updateXScale(svg, info);

            this.scale.y.domain([
                d3.min(data, this.getMinValue),
                d3.max(data, this.getMaxValue)
            ]);
        },

        addAxis: function(svg) {
            this.addXAxis(svg);
            this.addYAxis(svg);
        },

        addXAxis: function(svg) {
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.getInnerHeight() + ")")
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
                if(!response) {
                    that.unmask();
                    that.error("Component could not be loaded.");

                    return;
                }

                that.unmask();
                that.parseInfos(response.info);
                that.createDomain(that.svg, response.data, response.info);
                that.handleData(that.svg, response);
            });
        }

    });

}());
