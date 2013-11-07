var CodeChurn;

(function() {

    CodeChurn = Graph.extend({

        init: function(target, attrs) {
            this._super("churn", target, attrs);
        },

        setup: function(url) {
            var x = d3.time.scale().range([0, this.width]);
            var y = d3.scale.linear().range([this.height, 0]);

            var xAxis = d3.svg.axis().scale(x).orient("bottom");
            var yAxis = d3.svg.axis().scale(y).orient("left");

            var area = d3.svg.area()
                .x(function(d) {
                    return x(d.date);
                })
                .y0(this.height)
                .y1(function(d) {
                    return y(d.added);
                });

            var svg = d3.select(this.dom.get(0)).append("svg")
                .attr("width", this.width + this.margins.left + this.margins.right)
                .attr("height", this.height + this.margins.top + this.margins.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margins.left + "," + this.margins.top + ")");

            var that = this;

            d3.json(url, function(data) {
                data.forEach(function(d) {
                    d.date = new Date(d.date);
                });

                x.domain(d3.extent(data, function(d) {
                    return d.date;
                }));
                y.domain([0, d3.max(data, function(d) {
                    return d.added;
                })]);

                svg.append("path")
                    .datum(data)
                    .attr("class", "area")
                    .attr("d", area);

                svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0, " + that.height + ")")
                    .call(xAxis);

                svg.append("g")
                    .attr("class", "y axis")
                    .call(yAxis);
            });
        }

    });

    CodeChurn.auto = function(target, attrs) {
        $(target || ".churn").each(function() {
            new CodeChurn(this, attrs);
        });
    };

}());
