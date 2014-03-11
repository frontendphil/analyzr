ns("plugins");

(function() {

    analyzr.plugins.DetailedExperts = analyzr.core.Component.extend({

        init: function(target) {
            this._super("uberexperts", target);

            this.dom.append("<div class='authors' />");

            var that = this;

            this.filter = new analyzr.plugins.Filter(this.dom, function() {
                that.setup(that.url + "?" + this.toQueryString(), that.branch);
            });
        },

        updateFilter: function(info) {
            this.filter.update({
                languages: info.languages,
                language: info.options.language,
                startDate: info.options.startDate || info.options.minDate,
                endDate: info.options.endDate || info.options.maxDate
            });
        },

        clean: function() {
            this.dom.find(".authors").html("");
        },

        grab: function(data, container) {
            var item = data.shift();

            if(!item) {
                return;
            }

            var that = this;

            analyzr.core.data.get(item.href, {
                success: function(author) {
                    container.append(
                        "<li>" +
                            "<a href='" + that.branch + author.view + "'>" +
                                author.rep.name +
                            "</a>" +
                            "<span class='score'>(" + item.score + ")</span>" +
                        "</li>"
                    );

                    that.grab(data, container);
                }
            });
        },

        render: function(data) {
            this.clean();

            var container = $("<ol />");

            this.grab(data.slice(), container);

            this.dom.find(".authors").append(container);
        },

        handleData: function(response) {
            this.updateFilter(response.info);

            this.render(response.data);
        }

    });

}());
