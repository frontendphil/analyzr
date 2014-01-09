
ns("plugins");

(function() {

    analyzr.plugins.Filter = analyzr.core.Observeable.extend({

        init: function(target, clb) {
            this._super();

            this.dom = $(target);
            this.params = {};

            this.initComponent(clb);
        },

        update: function(options) {
            var files = options.files || [];

            this.updateFileSelector(files);
            this.updateLanguageSelector(options.languages, options.language);
            this.updateDatePicker(options.startDate, options.endDate);

            if(files.length === 0) {
                return;
            }

            this.raise("file.selected", files[0].name);
        },

        formatDate: function(date) {
            return date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getUTCFullYear();
        },

        changeParam: function(key, value) {
            this.params[key] = value;
        },

        toQueryString: function() {
            var params = [];

            $.each(this.params, function(key, value) {
                params.push(key + "=" + value);
            });

            return params.join("&");
        },

        initFilters: function() {
            var container = $("<div class='filters col-sm-10 col-lg-10 col-md-10' />");

            var mandatory = $("<div class='row' />");
            var optional = $("<div class='row' />");

            this.createDatePicker(mandatory);
            var language = this.createLanguageSelector();
            var packages = this.createPackageSelector();
            var files = this.createFileSelector();

            mandatory.append(language);
            optional.append(packages, files);

            container.append(mandatory, optional);

            return container;
        },

        initComponent: function(clb) {
            var container = $(
                "<form class='form-inline' role='form'>" +
                    "<div class='row'></div>" +
                "</form>"
            );

            var filters = this.initFilters();
            var button = this.createUpdateButton(clb);

            container.find(".row").append(filters, button);

            this.dom.append(container);
        },

        createUpdateButton: function(clb) {
            var button = $(
                "<div class='col-sm-2 col-lg-2 col-md-2'>" +
                    "<button class='btn btn-default update-filters'>Update filters</button>" +
                "</div>"
            );

            var that = this;

            button.find("button").click(function() {
                clb.apply(that);

                return false;
            });

            return button;
        },

        createPicker: function(element, value, clb) {
            var date = this.formatDate(new Date(value));
            var that = this;

            element.find("input").val(date);

            var button = element.find(".input-group-addon");
            button.data("date", date);
            button.datepicker({
                format: "dd/mm/yyyy",
                viewMode: "years"
            });
            button.on("changeDate", function(event) {
                if(event.viewMode !== "days") {
                    return;
                }

                element.find("input").val(that.formatDate(event.date));

                clb(event.date);
            });

            this.changeParam(element.data("rel"), value.toISOString());
        },

        createDatePicker: function(container) {
            var datepicker = function(rel) {
                return $(
                    "<div class='input-group date-" + rel + " col-sm-3 col-lg-3 col-md-3' data-rel='" + rel + "' >" +
                        "<input type='text' id='date-" + rel + "' class='form-control' readonly/>" +
                        "<span class='input-group-addon'>" +
                            "<i class='icon-calendar'></i>" +
                        "</span>" +
                    "</div>"
                );
            };

            var from = datepicker("from");
            var to = datepicker("to");

            container.append(from, to);
        },

        updateDatePicker: function(start, end) {
            var that = this;

            this.createPicker(this.dom.find(".date-from"), start, function(date) {
                that.changeParam("from", date.toISOString());
            });

            this.createPicker(this.dom.find(".date-to"), end, function(date) {
                that.changeParam("to", date.toISOString());
            });
        },

        createSelect: function(kind, values, clb) {
            values = values || [];

            var cls = "filter-" + kind.replace(" ", "-").toLowerCase();

            var container = this.dom.find("." + cls);
            var select = container.find("select");

            if(container.length === 0) {
                container = $("<div class='input-group col-sm-3 col-lg-3 col-md-3 " + cls + "' />");
                select = $(
                    "<select class='form-control'>" +
                        "<option value=''>" + kind.capitalize() + "</option>" +
                        "<option value=''>----</option>" +
                        // "<option value='all'>All</option>" +
                    "</select>"
                );

                container.append(select);
            }

            select.find("option").each(function() {
                var option = $(this);
                var value = option.attr("value");

                if(value) {
                    option.remove();
                }
            });

            $.each(values, function() {
                var item = clb(this);

                if(!item) {
                    return;
                }

                select.append(
                    "<option value='" + item.value + "'>" +
                        item.text +
                    "</option>"
                );
            });

            container.val = function() {
                select.val.apply(select, arguments);
            };

            container.change = function() {
                select.change.apply(select, arguments);
            };

            return container;
        },

        createLanguageSelector: function() {
            var select = this.createSelect("language");

            var that = this;

            select.change(function() {
                if(!this.value) {
                    return;
                }

                that.changeParam("language", this.value);
            });

            return select;
        },

        updateLanguageSelector: function(languages, value) {
            var select = this.createSelect("language", languages, function(language) {
                return {
                    value: language.toString(),
                    text: language.toString()
                };
            });

            if(value) {
                select.val(value);
            }
        },

        getCurrentFile: function() {
            return this.currentFile;
        },

        createFileSelector: function() {
            var select = this.createSelect("file");

            var that = this;

            select.change(function() {
                that.currentFile = that.files[this.value];

                that.raise("file.selected", this.value);
            });

            return select;
        },

        getCurrentPackage: function() {
            return this.currentPackage;
        },

        createPackageSelector: function() {
            if(this.dom.length === 0) {
                return;
            }

            var parse = function(parent, result, level) {
                level = level || 1;

                if(!result) {
                    result = [{
                        name: "/",
                        pkg: parent,
                        indent: ""
                    }];
                }

                $.each(parent.rep.children, function() {
                    result.push({
                        name: this.rep.name.replace(parent.rep.name, ""),
                        pkg: this,
                        indent: "|&nbsp;&nbsp;".repeat(level)
                    });

                    parse(this, result, level + 1);
                });

                return result;
            };

            var that = this;

            this.packages = {};

            $.ajax(this.dom.data("branch") + this.dom.data("author") + "/packages", {
                success: function(root) {
                    var children = parse(root);

                    that.createSelect("package", children, function(child) {
                        that.packages[child.pkg.href] = child.pkg;

                        return {
                            value: child.pkg.href,
                            text: child.indent + child.name
                        };
                    });
                }
            });

            var select = this.createSelect("package");

            select.change(function() {
                if(!this.value) {
                    return;
                }

                that.currentPackage = that.packages[this.value];

                that.changeParam("package", this.value.replace("/package/", ""));
            });

            return select;
        },

        updateFileSelector: function(files) {
            this.files = {};

            var that = this;

            $.each(files, function() {
                that.files[this.name] = this;
            });

            var select = this.createSelect("file", files, function(file) {
                var deleted = "";

                if(file.deleted) {
                    deleted = " - DELETED";
                }

                return {
                    value: file.name,
                    text: file.name + " (" + file.count + ")" + deleted
                };
            });

            if(files.length === 0) {
                select.hide();
            } else {
                select.show();

                var value = files[0].name;
                select.val(value);

                this.raise("file.selected", value);
            }
        }

    });

}());
