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
            var createTH = function(abbr, description) {
                return "<th>" +
                    "<i class='icon-exchange'></i> " +
                    "<abbr title='" + description + "'>" + abbr + "</abbr>" +
                "</th>";
            };

            var table = $(
                "<table class='table'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th>Package</th>" +
                            "<th>Name</th>" +
                            "<th>Change</th>" +
                            createTH("CC", "Cyclomatic Complexity Delta") +
                            createTH("HSV", "Halstead Volume Delta") +
                            createTH("HSD", "Halstead Difficulty Delta") +
                            createTH("FI", "Fan In Delta") +
                            createTH("FO", "Fan Out Delta") +
                            createTH("SLOC", "Source Lines of Code Delta") +
                            createTH("HK", "Information Flow Delta") +
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

                var complexity = that.parseMetrics(this.rep.complexity);
                var structure = that.parseMetrics(this.rep.structure);
                var packageName = this.rep["package"];

                if(that.pkg) {
                    packageName = packageName.replace(that.pkg.rep.name, "...");
                }

                body.append($(
                    "<tr>" +
                        "<td>" + packageName + "</td>" +
                        "<td>" + this.rep.name + "</td>" +
                        "<td class='delta'>" + this.rep.changeType + "</td>" +
                        createTD(complexity, "Cyclomatic Complexity") +
                        createTD(complexity, "Halstead Volume") +
                        createTD(complexity, "Halstead Difficulty") +
                        createTD(structure, "Fan In") +
                        createTD(structure, "Fan Out") +
                        createTD(structure, "SLOC") +
                        createTD(structure, "HK") +
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

            this.clear();

            this._super();
        },

        clear: function() {
            if(!this.dom) {
                return;
            }

            this.dom.remove();

            delete this.dom;
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
