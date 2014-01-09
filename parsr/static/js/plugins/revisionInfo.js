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
                            "<th>" +
                                "<i class='icon-exchange'></i> " +
                                "<abbr title='Cyclomatic Complexity Delta'>CC</abbr>" +
                            "</th>" +
                            "<th>" +
                                "<i class='icon-exchange'></i> " +
                                "<abbr title='Halstead Volume Delta'>HSV</abbr>" +
                            "</th>" +
                            "<th>" +
                                "<i class='icon-exchange'></i> " +
                                "<abbr title='Halstead Difficulty Delta'>HSD</abbt>" +
                            "</th>" +
                            "<th>" +
                                "<i class='icon-exchange'></i> " +
                                "<abbr title='Halstead Effort Delta'>HSE</abbr>" +
                            "</th>" +
                        "</tr>" +
                    "</thead>" +
                    "<tbody></tbody>" +
                "</table>"
            );

            var body = table.find("tbody");
            var that = this;

            var createTD = function(metrics, metric) {
                return "" +
                    "<td class='delta " + metrics[metric + " Delta"].cls + "'>" +
                        "<abbr title='" + metrics[metric].value + "'>" +
                            metrics[metric + " Delta"].value +
                        "</abbr>" +
                    "</td>";
            };

            $.each(files, function() {
                if(that.file && that.file.name !== "all") {
                    if(that.file.name !== this.rep["package"] + "/" + this.rep.name) {
                        return;
                    }
                }

                var metrics = that.parseMetrics(this.rep.complexity);
                var packageName = this.rep["package"];

                if(that.pkg) {
                    packageName = packageName.replace(that.pkg.rep.name, "...");
                }

                body.append($(
                    "<tr>" +
                        "<td>" + packageName + "</td>" +
                        "<td>" + this.rep.name + "</td>" +
                        "<td class='delta'>" + this.rep.changeType + "</td>" +
                        createTD(metrics, "Cyclomatic Complexity") +
                        createTD(metrics, "Halstead Volume") +
                        createTD(metrics, "Halstead Difficulty") +
                        createTD(metrics, "Halstead Effort") +
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

                th.width(Math.max(ref.width(), th.width()));
            });
        },

        show: function(pkg, file) {
            this.pkg = pkg;
            this.file = file;

            this._super();
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
                    content.append(
                        "<h5>" +
                            "<time datetime='" + revision.rep.date + "'>" +
                                revision.rep.date +
                            "</time>" +
                        "</h5>"
                    );

                    var fileChanges = that.createFileChanges(revision.rep.files);
                    content.append(fileChanges);

                    that.layout();
                }
            });
        }

    });

}());
