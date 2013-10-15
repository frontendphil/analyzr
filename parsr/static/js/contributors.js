var Contributors;

(function() {

    var LOOK_AROUND = 3;

    Contributors = Class.extend({
        init: function(target) {
            this.dom = $(target);

            var branch = this.dom.data("branch");

            this.setup(this.getUrl(branch), branch);
        },

        getUrl: function(branch, page) {
            var url = "/contributors/branch/" + branch;

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
                var url = that.getUrl(branch, page);

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

        createPages: function(pagination, data, branch) {
            var back = this.getLookBehind(data.page, LOOK_AROUND);
            var forward = this.getLookAhead(data.page, data.pages, back < 3 ? LOOK_AROUND + (LOOK_AROUND - back) : LOOK_AROUND);

            var i, page, length;
            for(i = data.page - back, length = data.page + forward; i < length; i = i + 1) {
                page = this.createListEntry(i + 1, i + 1);

                if(data.page === i + 1) {
                    page.addClass("disabled");
                }

                pagination.append(page);

                this.createClickHandler(page, branch, i + 1);
            }
        },

        createPagination: function(data, branch) {
            var pagination = $("<ul class='pagination' />");

            var first = this.createListEntry(0, "<i class='icon-double-angle-left'></i>");
            var previous = this.createListEntry(data.page - 1, "<i class='icon-angle-left'></i>");

            if(!data.hasPrevious) {
                previous.addClass("disabled");
                first.addClass("disabled");
            }

            this.createClickHandler(previous, data.page - 1);

            pagination.append(first, previous);

            this.createPages(pagination, data, branch);

            var next = this.createListEntry(data.page + 1, "<i class='icon-angle-right'></i>");
            var last = this.createListEntry(data.pages, "<i class='icon-double-angle-right'></i>");

            if(!data.hasNext) {
                next.addClass("disabled");
                last.addClass("disabled");
            }

            this.createClickHandler(next, branch, data.page + 1);

            pagination.append(next, last);

            return pagination;
        },

        clear: function() {
            this.dom.html("");
        },

        createTable: function(data, branch) {
            var table = $(
                "<table class='table table-hover'>" +
                    "<thead>" +
                        "<tr>" +
                            "<th class='rank'>#</td>" +
                            "<th>Name</th>" +
                            "<th class='revisions'>Revisions</th>" +
                        "<tr>" +
                    "</thead>" +
                "</table>"
            );

            var body = $("<tbody />");
            table.append(body);

            $.each(data.authors, function(index) {
                var entry = $(
                    "<tr>" +
                        "<td>" + ((data.perPage * (data.page - 1)) + index + 1) + "</td>" +
                        "<td>" +
                            "<a href='/author/" + this.id + "/branch/" + branch + "'>" + this.name + "</a>" +
                        "</td>" +
                        "<td>" + this.count + "</td>" +
                    "</tr>"
                );

                body.append(entry);
            });

            return table;
        },

        setup: function(url, branch) {
            var that = this;

            $.ajax(url, {
                success: function(data) {
                    that.clear();

                    var table = that.createTable(data, branch);
                    var pagination = that.createPagination(data, branch);

                    that.dom.append(table, pagination);
                }
            });
        }
    });

    Contributors.auto = function(target) {
        $(target || ".contributors").each(function() {
            new Contributors(this);
        });
    };

}());
