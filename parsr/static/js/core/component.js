ns("core");

(function() {

    analyzr.core.Component = analyzr.core.Observable.extend({

        init: function(action, target) {
            this._super();

            this.dom = $(target);

            this.branch = this.dom.data("branch");
            var author = this.dom.data("author");

            this.url = this.getUrl(action, this.branch, author);
        },

        getUrl: function(action, branch, author) {
            var url = branch;

            if(author) {
                url = url + author;
            }

            return url + "/" + action;
        },

        mask: function(text) {
            this.elementMask = new analyzr.core.Mask(this.dom, text);
            this.elementMask.show();
        },

        unmask: function() {
            this.elementMask.remove();
        },

        error: function(msg) {
            this.mask(msg);
            this.elementMask.hideSpinner();
        },

        load: function() {
            if(this.dom.length === 0) {
                return;
            }

            this.setup(this.url, this.branch);
        },

        setup: function(url, branch) {
            var that = this;

            this.mask("Loading...");

            analyzr.core.data.get(url, {
                success: function(data) {
                    that.unmask();
                    that.handleData(data, branch);
                }
            });
        },

        handleData: function() {}

    });

}());
