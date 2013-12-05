var Contributors;

(function() {

    var LOOK_AROUND = 3;

    var LANGUAGE_MAPPINGS = {
        "x-java-source": "java",
        "x-java": "java",
        "javascript": "js",
        "x-sql": "sql",
        "x-python": "py",
        "html": "html"
    };

    Contributors = Component.extend({

        init: function(target) {
            this._super("contributors", target);
        },

        getUrl: function(action, branch, page) {
            var url = branch + "/" + action;

            if(!page) {
                return url;
            }

            return url + "?page=" + page;
        },

        createListEntry: function(page, title) {
            return $(
                "<li>" +
                    "<a href='?page=" + page + "'>" + title + "</a>" +
                "</li>"
            );
        },

        createClickHandler: function(element, branch, page) {
            var that = this;

            element.find("a").click(function() {
                var url = that.getUrl("contributors", branch, page);

                that.setup(url, branch);

                return false;
            });
        },

        getLookBehind: function(page, threshold) {
            var i = 0;

            while(page > 0 && i <= threshold) {
                page = page - 1;
                i = i + 1;
            }

            return i;
        },

        getLookAhead: function(page, pages, threshold) {
            var i = 0;

            threshold = Math.min(pages - page, threshold);

            while(page < pages, i < threshold) {
                page = page + 1;
                i = i + 1;
            }

            return i;
        },

        createPages: function(pagination, info, branch) {
            var back = this.getLookBehind(info.page, LOOK_AROUND);
            var forward = this.getLookAhead(info.page, info.pages, back < 3 ? LOOK_AROUND + (LOOK_AROUND - back) : LOOK_AROUND);

            var i, page, length;
            for(i = info.page - back, length = info.page + forward; i < length; i = i + 1) {
                page = this.createListEntry(i + 1, i + 1);

                if(info.page === i + 1) {
                    page.addClass("disabled");
                }

                pagination.append(page);

                this.createClickHandler(page, branch, i + 1);
            }
        },

        createPagination: function(info, branch) {
            var pagination = $("<ul class='pagination' />");

            var first = this.createListEntry(0, "<i class='icon-double-angle-left'></i>");
            var previous = this.createListEntry(info.page - 1, "<i class='icon-angle-left'></i>");

            if(!info.hasPrevious) {
                previous.addClass("disabled");
                first.addClass("disabled");
            }

            this.createClickHandler(previous, info.page - 1);

            pagination.append(first, previous);

            this.createPages(pagination, info, branch);

            var next = this.createListEntry(info.page + 1, "<i class='icon-angle-right'></i>");
            var last = this.createListEntry(info.pages, "<i class='icon-double-angle-right'></i>");

            if(!info.hasNext) {
                next.addClass("disabled");
                last.addClass("disabled");
            }

            this.createClickHandler(next, branch, info.page + 1);

            pagination.append(next, last);

            return pagination;
        },

        clear: function() {
            this.dom.html("");
        },

        createTable: function(authors, info, branch) {
            var table = $(
                "<table class='table table-hover'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th class='rank'>#</td>" +
                            "<th></th>" +
                            "<th></th>" +
                            "<th>Name</th>" +
                            "<th class='revisions'>Revisions</th>" +
                        "<tr>" +
                    "</thead>" +
                "</table>"
            );

            var body = $("<tbody />");
            table.append(body);

            $.each(authors, function(index) {
                var language = "N/A";

                if(this.rep.primeLanguage) {
                    language = LANGUAGE_MAPPINGS[this.rep.primeLanguage.mimetype];
                }

                var entry = $(
                    "<tr>" +
                        "<td class='rank'>" + ((info.perPage * (info.page - 1)) + index + 1) + "</td>" +
                        "<td class='lang'>" +
                            (language || "") +
                        "</td>" +
                        "<td class='avatar' style='background-image:url(" + this.rep.icon + ")'></td>" +
                        "<td>" +
                            "<a href='" + branch + this.href + "'>" + this.rep.name + "</a>" +
                        "</td>" +
                        "<td>" + this.rep.count + "</td>" +
                    "</tr>"
                );

                body.append(entry);
            });

            return table;
        },

        handleData: function(response, branch) {
            this.clear();

            var table = this.createTable(response.data, response.info, branch);
            var pagination = this.createPagination(response.info, branch);

            this.dom.append(table, pagination);
        }

    });
}());
