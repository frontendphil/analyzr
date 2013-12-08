(function() {

    if(!window.analyzr) {
        window.analyzr = {};
    }

    window.ns = function(packages) {
        packages = packages.split(".");

        var createNS = function(packages, current) {
            var pkg = packages.shift();

            if(!pkg) {
                return;
            }

            if(pkg === "analyzr") {
                return createNS(packages, current);
            }

            if(!current) {
                current = window.analyzr;
            }

            if(!current[pkg]) {
                current[pkg] = {};
            }

            return createNS(packages, current[pkg]);
        };

        createNS(packages);
    };

    ns("utils");

    var _round = Math.round;

    Math.round = function(number, precision) {
        precision = Math.abs(parseInt(precision, 10)) || 0;
        var coefficient = Math.pow(10, precision);

        return _round(number * coefficient) / coefficient;
    };

    analyzr.utils.svgToPNG = function(target) {
        var canvas = $("<canvas />");

        var element = target.clone();

        var inlineStyles = function(parent) {
            var styles = analyzr.utils.css(parent);
            parent.css(styles);

            $.each(parent.children(), function() {
                inlineStyles($(this));
            });
        };

        inlineStyles(element);

        var ctx = canvas.get(0).getContext("2d");

        $("body").append(canvas);

        var serializer = new XMLSerializer();
        var data = serializer.serializeToString(element.get(0));
        var DOMURL = window.URL || window.webkitURL || window;

        var img = new Image();
        var svg = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        var url = DOMURL.createObjectURL(svg);

        img.onload = function() {
            ctx.drawImage(img, 0, 0);
            DOMURL.revokeObjectURL(svg);
        };

        img.src= url;
    };

    analyzr.utils.css = function(a) {
        var sheets = document.styleSheets, o = {};
        for (var i in sheets) {
            var rules = sheets[i].rules || sheets[i].cssRules;
            for (var r in rules) {
                if (a.is(rules[r].selectorText)) {
                    o = $.extend(o, css2json(rules[r].style), css2json(a.attr('style')));
                }
            }
        }
        return o;
    };

    var css2json = function(css) {
        var s = {}, i;
        if (!css) {
            return s;
        }

        if (css instanceof CSSStyleDeclaration) {
            for (i in css) {
                if ((css[i]).toLowerCase) {
                    s[(css[i]).toLowerCase()] = (css[css[i]]);
                }
            }
        } else if (typeof css === "string") {
            css = css.split("; ");
            for (i in css) {
                var l = css[i].split(": ");
                s[l[0].toLowerCase()] = (l[1]);
            }
        }
        return s;
    };

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

            var months = Math.floor(weeks/4.3);

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
                months: months,
                years: years
            };
        };
    }

}());
