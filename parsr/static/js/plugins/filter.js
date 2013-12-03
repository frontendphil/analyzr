var Filter;

(function() {

    Filter = Observeable.extend({

        init: function(target, clb) {
            this._super();

            this.dom = $(target);
            this.params = {};

            this.initComponent(clb);
        },

        update: function(options) {
            var files = options.files;

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
            var container = $("<div class='filters col-lg-10 col-md-10' />");

            this.createDatePicker(container);
            var language = this.createLanguageSelector();
            var files = this.createFileSelector();

            container.append(language, files);

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
                "<div class='col-lg-2 col-md-2'>" +
                    "<button class='btn btn-default update-filters'>Update</button>" +
                "</div>"
            );

            var that = this;

            button.on("click", function() {
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

            this.changeParam(element.data("rel"), date);
        },

        createDatePicker: function(container) {
            var datepicker = function(rel) {
                return $(
                    "<div class='input-group date-" + rel + " col-lg-3 col-md-3' data-rel='" + rel + "' >" +
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

            this.createPicker($(".date-from"), start, function(date) {
                that.changeParam("from", date.toISOString());
            });

            this.createPicker($(".date-to"), end, function(date) {
                that.changeParam("to", date.toISOString());
            });
        },

        createSelect: function(kind, values, clb) {
            values = values || [];

            var cls = "filter-" + kind.replace(" ", "-").toLowerCase();

            var container = this.dom.find("." + cls);
            var select = container.find("select");

            if(container.length === 0) {
                container = $("<div class='input-group col-lg-1 col-md-3 " + cls + "' />");
                select = $(
                    "<select class='form-control'>" +
                        "<option value=''>" + kind.capitalize() + "</option>" +
                        "<option value=''>----</option>" +
                        "<option value='all'>All</option>" +
                    "</select>"
                );

                container.append(select);
            }

            select.find("option").each(function() {
                var option = $(this);
                var value = option.attr("value");

                if(value && value !== "all") {
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

        createFileSelector: function() {
            var select = this.createSelect("file");

            var that = this;

            select.change(function() {
                that.raise("file.selected", this.value);
            });

            return select;
        },

        updateFileSelector: function(files) {
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
            }
        }

    });

}());
