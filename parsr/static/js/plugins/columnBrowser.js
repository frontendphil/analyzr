ns("analyzr.plugins");

(function() {

    analyzr.plugins.ColumnBrowser = analyzr.core.Observable.extend({

        init: function(target, attrs) {
            this._super();

            this.dom = $(target);

            this.height = attrs.height || 300;

            this.initBrowser(attrs.root);
        },

        initBrowser: function(root) {
            var container = $("<div class='column-browser' />");

            this.dom.append(container);

            var list = this.getListContainer();

            container.append(list);

            this.loadData(root, list);
        },

        getListContainer: function() {
            var container = $("<div class='children' />");

            container.css({
                height: this.height
            });

            return container;
        },

        loadData: function(parent, container) {
            var list = $("<ul />");
            list.css({
                height: this.height
            });

            container.append(list);

            var that = this;

            var children = parent.rep.children.sort(function(a, b) {
                if(a.rep.name.toLowerCase() < b.rep.name.toLowerCase()) {
                    return -1;
                }

                if(a.rep.name.toLowerCase() > b.rep.name.toLowerCase()) {
                    return 1;
                }

                return 0;
            });

            $.each(children, function() {
                var name = this.rep.name.replace(parent.rep.name, "").replace("/", "");

                if(!name) {
                    return;
                }

                var entry = $("<li>" + name + "</li>");
                var child = this;

                if(this.rep.children.length === 0) {
                    entry.addClass("leaf");
                }

                entry.click(function() {
                    var link = $(this);

                    if(link.hasClass("active")) {
                        link.removeClass("active");
                        that.raise("select", parent.href);
                        that.reset(container);

                        return;
                    }

                    that.reset(container);

                    that.raise("select", child.href);

                    link.addClass("active");

                    if(link.hasClass("leaf")) {
                        return;
                    }

                    var list = that.getListContainer();
                    container.append(list);

                    that.loadData(child, list);
                    that.updateScroll();
                });

                list.append(entry);
            });
        },

        updateScroll: function() {
            var browser = this.dom.find(".column-browser");

            browser.animate({
                scrollLeft: browser.width()
            }, 500);
        },

        reset: function(container) {
            container.find(".active").each(function() {
                $(this).removeClass("active");
            });
            container.find(".children").remove();
        }

    });

}());
