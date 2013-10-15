var Component;

(function() {

    Component = Class.extend({

        init: function(base, target) {
            this.dom = $(target);

            var branch = this.dom.data("branch");
            var author = this.dom.data("author");

            var url = this.getUrl(base, branch, author);

            this.setup(url, branch);
        },

        getUrl: function(base, branch, author) {
            var url = "/" + base + "/branch/" + branch;

            if(author) {
                url = url + "/author/" + author;
            }

            return url;
        },

        mask: function(text) {
            this.elementMask = new Mask(this.dom, text);
            this.elementMask.show();
        },

        unmask: function() {
            this.elementMask.remove();
        },

        setup: function(url, branch) {
            var that = this;

            this.mask("Loading...");

            $.ajax(url, {
                success: function(data) {
                    that.unmask();
                    that.handleData(data, branch);
                }
            });
        },

        handleData: function() {}

    });

}());
