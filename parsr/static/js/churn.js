var CodeChurn;

(function() {

    CodeChurn = Graph.extend({

        init: function(target, attrs) {
            this._super("churn", target, attrs);
        },

        beforeRequest: function() {
            var that = this;

            this.added = d3.svg.area()
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y1(function(d) {
                    return that.scale.y(d.added);
                })
                .y0(function() {
                    return that.scale.y(0);
                });

            this.removed = d3.svg.area()
                .x(function(d) {
                    return that.scale.x(d.date);
                })
                .y1(function() {
                    return that.scale.y(0);
                })
                .y0(function(d) {
                    return that.scale.y(-1 * d.removed);
                });
        },

        handleData: function(svg, data) {
            data.forEach(function(d) {
                d.date = new Date(d.date);
            });

            svg.append("path")
                .datum(data)
                .attr("class", "area added")
                .attr("d", this.added);

            svg.append("path")
                .datum(data)
                .attr("class", "area removed")
                .attr("d", this.removed);
        },

        getMaxValue: function(d) {
            return d.added;
        },

        getMinValue: function(d) {
            return -1 * d.removed;
        }

    });

    CodeChurn.auto = function(target, attrs) {
        $(target || ".churn").each(function() {
            new CodeChurn(this, attrs);
        });
    };

}());
