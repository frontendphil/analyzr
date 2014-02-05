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
                var entry = that.createChild(this, parent, container);

                list.append(entry);
            });
        },

        createChild: function(child, parent, container) {
            var name = child.rep.name.replace(parent.rep.name, "").replace("/", "");

            if(!name) {
                return;
            }

            var entry = $("<li>" + name + "</li>");

            if(child.rep.children.length === 0) {
                entry.addClass("leaf");
            }

            var that = this;

            entry.click(function() {
                that.handleClick($(this), child, parent, container);
            });

            return entry;
        },

        handleClick: function(link, child, parent, container) {
            if(link.hasClass("active")) {
                link.removeClass("active");
                this.raise("select", parent);
                this.reset(container);

                return;
            }

            this.reset(container);

            this.raise("select", child);

            link.addClass("active");

            if(link.hasClass("leaf")) {
                return;
            }

            var list = this.getListContainer();
            container.append(list);

            this.loadData(child, list);
            this.updateScroll();
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
