var Utils;

(function() {

    if(!String.prototype.capitalize) {
        String.prototype.capitalize = function() {
            if(!this) {
                return "";
            }

            var firstLetter = this.slice(0, 1);

            return firstLetter.toUpperCase() + this.slice(1);
        };
    }

    var MS_TO_SEC = function(ms) {
        return ms / 1000;
    };

    var SEC_TO_MS = function(sec) {
        return sec * 1000;
    };

    var MS_TO_MIN = function(ms) {
        return MS_TO_SEC(ms) / 60;
    };

    var MIN_TO_MS = function(min) {
        return SEC_TO_MS(min) * 60;
    };

    var MS_TO_HOURS = function(ms) {
        return MS_TO_MIN(ms) / 60;
    };

    var HOURS_TO_MS = function(hours) {
        return MIN_TO_MS(hours) * 60;
    };

    var MS_TO_DAYS = function(ms) {
        return MS_TO_HOURS(ms) / 24;
    };

    var DAYS_TO_MS = function(days) {
        return HOURS_TO_MS(days) * 24;
    };

    var MS_TO_WEEKS = function(ms) {
        return MS_TO_DAYS(ms) / 7;
    };

    var WEEKS_TO_MS = function(weeks) {
        return DAYS_TO_MS(weeks) * 7;
    };

    var MS_TO_YEARS = function(ms) {
        return MS_TO_WEEKS(ms) / 52;
    };

    var YEARS_TO_MS = function(years) {
        return WEEKS_TO_MS(years) * 52;
    };

    if(!Date.prototype.to) {
        Date.prototype.to = function(end) {
            var span = end - this;

            var years = Math.floor(MS_TO_YEARS(span));

            var overflowYears = span % YEARS_TO_MS(1);
            var weeks = Math.floor(MS_TO_WEEKS(overflowYears));

            var overflowWeeks = span % WEEKS_TO_MS(1);
            var days = Math.floor(MS_TO_DAYS(overflowWeeks));

            var overflowDays = span % DAYS_TO_MS(1);
            var hours = Math.floor(MS_TO_HOURS(overflowDays));

            var overflowHours = span % HOURS_TO_MS(1);
            var minutes = Math.floor(MS_TO_MIN(overflowHours));

            var overflowMinutes = span % MIN_TO_MS(1);
            var seconds = Math.floor(MS_TO_SEC(overflowMinutes));

            return {
                seconds: seconds,
                minutes: minutes,
                hours: hours,
                days: days,
                weeks: weeks,
                years: years
            };
        };
    }

}());
