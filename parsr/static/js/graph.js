var Graph;

(function() {

    Graph = Component.extend({

        init: function(base, target, attrs) {
            attrs = attrs || {};

            this.margins = this.createMargins(attrs.margins || {});

            this.width = attrs.width || $(target).width();
            this.height = attrs.height || 400;

            this.dom = $(target);
            this.svg = this.prepareSVG();

            this._super(base, target);
        },

        createMargins: function(margins) {
            return {
                top: margins.top || 0,
                left: margins.left || 0,
                bottom: margins.bottom || 0,
                right: margins.right || 0
            };
        },

        getInnerWidth: function() {
            return this.width - this.margins.left - this.margins.right;
        },

        getInnerHeight: function() {
            return this.height - this.margins.top - this.margins.bottom;
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
                x: d3.svg.axis().scale(x).orient("bottom"),
                y: d3.svg.axis().scale(y).orient("left")
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
        },

        addAxis: function(svg) {
            this.addXAxis(svg);
            this.addYAxis(svg);
        },

        addXAxis: function(svg) {
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.height + ")")
                .call(this.axis.x);
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

            d3.json(url, function(response) {
                that.prepareData(response);
                that.createDomain(response, that.getMinValue, that.getMaxValue);
                that.handleData(that.svg, response.data);
                that.addAxis(that.svg);
            });
        }

    });

}());