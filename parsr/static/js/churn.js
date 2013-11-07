var CodeChurn;

(function() {

    CodeChurn = Graph.extend({

        init: function(target, attrs) {
            this._super("churn", target, attrs);
        },

        beforeRequest: function() {
            var that = this;

            this.area = d3.svg.area()
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y0(this.height)
                .y1(function(d) {
                    return that.scale.y(d.added);
                });
        },

        handleData: function(svg, data) {
            svg.append("path")
                .datum(data)
                .attr("class", "area")
                .attr("d", this.area);
        },

        getYDomain: function(d) {
            return d.added;
        },

    });

    CodeChurn.auto = function(target, attrs) {
        $(target || ".churn").each(function() {
            new CodeChurn(this, attrs);
        });
    };

}());
