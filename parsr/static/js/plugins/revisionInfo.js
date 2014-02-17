ns("plugins");

(function() {

    var MAX_COLUMN_WIDTH = 300;

    analyzr.plugins.RevisionInfo = analyzr.plugins.Dialog.extend({

        init: function(revision) {
            this.revision = revision;

            this._super({
                width: 900,
                title: "Revision Info"
            });

            var that = this;

            // this.on("layout", function() {
            //     that.layoutTable();
            // });
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
                    "<abbr title='" + description.capitalize() + "'>" + abbr + "</abbr>" +
                "</th>";
            };

            var table = $(
                "<table class='table'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th>Package</th>" +
                            "<th>Name</th>" +
                            "<th>Change</th>" +
                            createTH("CC", "cyclomatic_complexity_delta") +
                            createTH("HSV", "halstead_volume_delta") +
                            createTH("HSD", "halstead_difficulty_delta") +
                            createTH("FI", "fan_in_delta") +
                            createTH("FO", "fan_out_delta") +
                            createTH("SLOC", "sloc_delta") +
                        "</tr>" +
                    "</thead>" +
                    "<tbody></tbody>" +
                "</table>"
            );

            var body = table.find("tbody");
            var that = this;

            var createTD = function(metrics, metric) {
                return "" +
                    "<td class='delta " + metrics[metric + "_delta"].cls + "'>" +
                        "<abbr title='" + metrics[metric].value + "'>" +
                            metrics[metric + "_delta"].value +
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
                        createTD(complexity, "cyclomatic_complexity") +
                        createTD(complexity, "halstead_volume") +
                        createTD(complexity, "halstead_difficulty") +
                        createTD(structure, "fan_in") +
                        createTD(structure, "fan_out") +
                        createTD(structure, "sloc") +
                    "</tr>"
                ));
            });

            return table;
        },

        findWidestColumn: function(index) {
            var max = 0;

            this.dom.find("tbody tr").each(function() {
                var row = $(this);
                var probe = row.find("td:nth-child(" + index + ")");

                max = Math.max(max, probe.outerWidth());
            });

            return Math.min(max, MAX_COLUMN_WIDTH);
        },

        setColumnWidth: function(index, width) {
            this.dom.find("tbody tr").each(function() {
                var row = $(this);

                var cell = row.find("td:nth-child(" + index + ")");
                cell.outerWidth(width);
            });
        },

        layoutTable: function() {
            var head = this.dom.find("thead");
            var body = this.dom.find("tbody");

            var that = this;

            head.find("th").each(function(index) {
                var th = $(this);
                var widest = that.findWidestColumn(index + 1);

                th.outerWidth(Math.max(widest, th.outerWidth()));
            });

            head.find("th").each(function(index) {
                var th = $(this);

                that.setColumnWidth(index + 1, th.outerWidth());
            });

            var width = 0;

            this.dom.find("table thead th").each(function() {
                width += $(this).outerWidth();
            });

            this.dom.find("table").width(width);
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

        layout: function() {
            var cHeight = Math.min(this.container.outerHeight(), window.innerHeight);
            var cWidth = Math.min(this.container.outerWidth(), window.innerWidth);

            var mHeight = this.dom.find(".body").outerHeight();
            var mWidth = this.dom.find(".body").outerWidth();

            var side = this.container.scrollLeft() + cWidth - mWidth;

            this.dom.find(".body").css({
                marginTop: this.container.scrollTop() + (cHeight / 2) - (mHeight / 2),
                marginLeft: side / 2,
                marginRight: side / 2
            });

            this.raise("layout");
        },

        render: function() {
            this._super();

            this.dom.addClass("revision-info");

            var body = this.dom.find(".body");

            body.find(".icon-spinner").show();
            body.find(".text").html("Loading revision data...");

            var that = this;
            var content = body.find(".content");

            analyzr.core.data.get(this.revision, {
                success: function(revision) {
                    content.html("");

                    content.append(
                        "<h3>" +
                            "<a href='" + revision.view + "' target='_blank'>" +
                                revision.rep.identifier +
                            "</a>" +
                        "</h3>"
                    );
                    content.append(
                        "<h5>" +
                            "<time datetime='" + revision.rep.date + "'>" +
                                revision.rep.date +
                            "</time>" +
                        "</h5>"
                    );

                    if(revision.rep.message) {
                        content.append("<div class='message well'>" + revision.rep.message.replace(/\n/g, "<br />") + "</div>");
                    }

                    analyzr.core.data.get(revision.rep.author, {
                        success: function(author) {
                            content.find("h5").append(" - Created by <emph>" + author.rep.name + "</emph>");
                        }
                    });

                    var fileChanges = that.createFileChanges(revision.rep.files);
                    content.append(fileChanges);

                    that.layoutTable();
                    that.layout();
                }
            });
        }

    });

}());
