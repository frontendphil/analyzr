define([
    "backbone",
    "underscore"
], function(
    Backbone,
    _
) {

    var WEEKDAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ];

    return Backbone.Model.extend({

        getHour: function(hour) {
            return this.get(hour.toString());
        },

        weekdays: function() {
            return WEEKDAYS;
        },

        hours: function() {
            return _.range(25);
        },

        getValue: function(day, hour) {
            return this.get(WEEKDAYS.indexOf(day).toString())[hour.toString()];
        },

        getMax: function() {
            return _.max(_.map(_.range(WEEKDAYS.length), function(day) {
                return _.max(this.get(day), function(value) {
                    return value;
                });
            }, this));
        }

    });

});
