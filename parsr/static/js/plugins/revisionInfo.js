ns("plugins");

(function() {

    analyzr.plugins.RevisionInfo = analyzr.plugins.Dialog.extend({

        init: function(revision) {
            this.revision = revision;

            this._super({
                width: 900
            });

            var that = this;

            this.on("layout", function() {
                that.layoutTable();
            });
        },

        parseMetrics: function(metrics) {
            var result = {};

            $.each(metrics, function(key, value) {
                result[key] = {
                    value: value,
                    cls: value > 0 ? "positive" : value < 0 ? "negative" : ""
                };
            });

            return result;
        },

        createFileChanges: function(files) {
            var table = $(
                "<table class='table'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th>Package</th>" +
                            "<th>Name</th>" +
                            "<th>Change</th>" +
                            "<th><i class='icon-exchange'></i> CC</th>" +
                            "<th><i class='icon-exchange'></i> HSV</th>" +
                            "<th><i class='icon-exchange'></i> HSD</th>" +
                            "<th><i class='icon-exchange'></i> HSE</th>" +
                        "</tr>" +
                    "</thead>" +
                    "<tbody></tbody>" +
                "</table>"
            );

            var body = table.find("tbody");
            var that = this;

            var createTD = function(metrics, metric) {
                return "" +
                    "<td class='delta " + metrics[metric].cls + "'>" +
                        metrics[metric].value +
                    "</td>";
            };

            $.each(files, function() {
                var metrics = that.parseMetrics(this.rep.complexity);

                body.append($(
                    "<tr>" +
                        "<td>" + this.rep["package"] + "</td>" +
                        "<td>" + this.rep.name + "</td>" +
                        "<td class='delta'>" + this.rep.changeType + "</td>" +
                        createTD(metrics, "cyclomaticComplexityDelta") +
                        createTD(metrics, "halsteadVolumeDelta") +
                        createTD(metrics, "halsteadDifficultyDelta") +
                        createTD(metrics, "halsteadEffortDelta") +
                    "</tr>"
                ));
            });

            return table;
        },

        layoutTable: function() {
            var head = this.dom.find("thead");
            var body = this.dom.find("tbody");

            var probe = body.find("tr:first-child").find("td");

            head.find("th").each(function(index) {
                var th = $(this);
                var ref = $(probe.get(index));

                var padding = parseInt(ref.css("padding"), 10);

                th.width(ref.width());
            });
        },

        render: function() {
            this._super();

            this.dom.addClass("revision-info");

            var body = this.dom.find(".body");

            body.find(".icon-spinner").show();
            body.find(".text").html("Loading revision data...");

            var that = this;
            var content = body.find(".content");

            $.ajax(this.revision, {
                success: function(revision) {
                    content.html("");

                    content.append("<h3>" + revision.rep.identifier + "</h3>");
                    content.append("<h5>" + revision.rep.date + "</h3>");

                    var fileChanges = that.createFileChanges(revision.rep.files);
                    content.append(fileChanges);

                    that.layout();
                }
            });
        }

    });

}());
