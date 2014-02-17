ns("plugins");

(function() {

    analyzr.plugins.Dialog = analyzr.core.Mask.extend({

        init: function(attrs) {
            attrs = attrs || {};

            this.attrs = attrs;

            this._super("body", attrs.text);

            this.width(attrs.width);
        },

        width: function(width) {
            if(!width) {
                return;
            }

            this.dom.find(".body").width(width);
        },

        close: function() {
            if(!this.dom) {
                return;
            }

            this.dom.remove();
        },

        standardButton: function() {
            var dismiss = $("<button class='btn btn-default'>Dismiss</button>");

            var that = this;

            dismiss.click(function() {
                that.remove();
            });

            this.dom.find(".actions").append(dismiss);
        },

        render: function() {
            this._super();

            this.initEvents();

            this.dom.addClass("dialog");

            var dialog = this.dom.find(".panel");
            var body = this.dom.find(".panel-body");

            if(this.attrs.title) {
                dialog.prepend("<div class='panel-heading'>" + this.attrs.title + "</div>");
            }

            if(!this.attrs.waiting) {
                this.dom.find(".icon-spinner").hide();
            }

            var actions = $("<div class='actions' />");
            body.append(actions);

            if(!this.attrs.actions || this.attrs.actions.length === 0) {
                this.standardButton();

                return;
            }

            var that = this;

            $.each(this.attrs.actions, function() {
                var button = $("<button class='btn btn-default'>" + this.text + "</button>");
                var action = this;

                button.click(function() {
                    return action.handler(that);
                });

                if(this.cls) {
                    button.addClass(this.cls);
                }

                actions.append(button);
            });

            dialog.css({
                "marginTop": ($("body").height() / 2) - (dialog.height() / 2)
            });
        },

        initEvents: function() {
            var that = this;

            var handler = function(e) {
                if(e.which !== 27) {
                    // ESC key
                    return;
                }

                $(document).off("keydown", handler);

                that.close();
            };

            $(document).on("keydown", handler);
        }

    });

    analyzr.plugins.Dialog.confirm = function(text, clb) {
        var dialog = new analyzr.plugins.Dialog({
            text: text,
            title: "Please Confirm",
            actions: [
                {
                    text: "Cancel",
                    handler: function(dialog) {
                        dialog.close();
                    }
                },
                {
                    text: "Ok",
                    cls: "btn btn-primary",
                    handler: function(dialog) {
                        clb();
                        dialog.close();
                    }
                }
            ]
        });
        dialog.show();
    }

}());
