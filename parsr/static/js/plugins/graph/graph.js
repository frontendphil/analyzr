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

        createMargins: function(margins) {
            return {
                top: margins.top || 0,
                left: margins.left || 0,
                bottom: margins.bottom || 0,
                right: margins.right || 0
            };
        },

        updateFilters: function(files, info) {
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

        prepareData: function(response) {
            response.info.dates = response.info.dates.map(function(date) {
                return new Date(date);
            });
        },

        setup: function(url) {
            this.beforeRequest();

            var that = this;

            this.mask("Loading graph data...");

            d3.json(url, function(response) {
                that.unmask();
                that.prepareData(response);
                that.createDomain(response, that.getMinValue, that.getMaxValue);
                that.handleData(that.svg, response);
                that.addAxis(that.svg);
            });
        }

    });

}());
