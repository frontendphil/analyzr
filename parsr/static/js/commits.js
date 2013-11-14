var CommitHistory;

(function() {

    CommitHistory = Graph.extend({

        init: function(target, attrs) {
            this._super("commits", target, attrs);
        },

        prepareData: function(data, month, year) {
            var result = [];

            $.each(d3.range(0, 31), function() {
                var day = this + 1;

                result.push({
                    day: day,
                    count: (data[year][month][day] || {}).commits || 0
                });
            });

            return result;
        },

        getYears: function(data) {
            return d3.map(data).keys();
        },

        getMonths: function(data, year) {
            return d3.map(data[year]).keys();
        },

        prepareSVG: function() {},

        getPastMonth: function(data, year, month) {
            var months = this.getMonths(data, year);

            var index = months.indexOf(month);

            if(index > 0) {
                return {
                    year: year,
                    month: months[index - 1]
                };
            }

            var years = this.getYears(data);

            index = years.indexOf(year);

            if(index > 0) {
                year = years[index - 1];
                months = this.getMonths(data, year);

                return {
                    year: year,
                    month: months[months.length - 1]
                };
            }

            return {};
        },

        getNextMonth: function(data, year, month) {
            var months = this.getMonths(data, year);

            var index = months.indexOf(month);

            if(index < months.length - 1) {
                return {
                    year: year,
                    month: months[index + 1]
                };
            }

            var years = this.getYears(data);

            index = years.indexOf(year);

            if(index < years.length - 1) {
                year = years[index + 1];
                months = this.getMonths(data, year);

                return {
                    year: year,
                    month: months[0]
                };
            }

            return {};
        },

        setup: function(url) {
            var that = this;

            var barWidth = this.getInnerWidth() / 31 - 1;

            var x = d3.scale.ordinal().rangeRoundBands([0, this.getInnerWidth()], 0.1);
            var y = d3.scale.linear().range([this.getInnerHeight(), 0]);

            var xAxis = d3.svg.axis().scale(x).orient("bottom");
            var yAxis = d3.svg.axis().scale(y).orient("left").tickSize(-this.getInnerWidth());

            var svg = d3.select(this.dom.get(0)).append("svg")
                .attr("class", "chart")
                .attr("width", this.width + this.margins.left + this.margins.right)
                .attr("height", this.height + this.margins.top + this.margins.bottom)
                .append("g")
                .attr("transform", "translate(" + this.margins.left + "," + this.margins.top + ")");

            var days = svg.append("g")
                .attr("class", "days")
                .attr("transform", "translate(" + (barWidth / 2) + ",0)");

            var title = svg.append("text")
                .attr("class", "title")
                .attr("dx", this.getInnerWidth())
                .attr("dy", -(this.margins.top / 2));

            var update = function(data, month, year, initial) {
                title.text(month + " / " + year);

                data = that.prepareData(data, month, year);

                days.selectAll(".bar")
                    .data(data)
                    .transition()
                    .duration(750)
                    .delay(200)
                    .attr("y", function(d) {
                        return y(d.count);
                    })
                    .attr("height", function(d) {
                        return that.getInnerHeight() - y(d.count);
                    });

                if(!initial) {
                    days.selectAll(".day text")
                        .data(data)
                        .transition()
                        .duration(200)
                        .style("opacity", 0);
                }

                days.selectAll(".day text")
                    .transition()
                    .duration(200)
                    .delay(initial ? 0 : 950)
                    .style("opacity", 1)
                    .text(function(d) {
                        return d.count;
                    });
            };

            d3.json(url, function(error, commits) {
                var data = d3.map(commits.data);

                var year = d3.max(data.keys());
                var month =  "" + d3.max(d3.map(data.get(year)).keys(), function(key) {
                    return parseInt(key);
                });

                x.domain(d3.range(1, 32));
                y.domain([0, commits.upper]);

                var day = days.selectAll(".bar")
                    .data(that.prepareData(commits.data, month, year))
                    .enter().append("g")
                    .attr("class", "day")
                    .attr("transform", function(d) {
                        return "translate(" + x(d.day) + ",0)";
                    });

                day.append("rect")
                    .attr("class", "bar")
                    .attr("x", -barWidth / 2)
                    .attr("width", barWidth);

                day.append("text")
                    .attr("y", that.getInnerHeight() - 4)
                    .text(function(d) {
                        return d.count;
                    });

                svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + that.getInnerHeight() + ")")
                    .call(xAxis);

                svg.append("g")
                    .attr("class", "y axis")
                    .call(yAxis);

                window.focus();
                d3.select(window).on("keydown", function() {
                    var date;

                    switch(d3.event.keyCode) {
                    case 37:
                        date = that.getPastMonth(commits.data, year, month);
                        break;
                    case 39:
                        date = that.getNextMonth(commits.data, year, month);
                        break;
                    }

                    if(!date) {
                        return;
                    }

                    if(!date.year && !date.month) {
                        return;
                    }

                    year = date.year || year;
                    month = date.month || month;

                    update(commits.data, month, year);
                });

                update(commits.data, month, year, true);
            });
        }

    });

    CommitHistory.auto = function(target, attrs) {
        $(target || ".commits").each(function() {
            new CommitHistory(this, attrs);
        });
    };

}());
