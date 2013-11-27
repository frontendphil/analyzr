var Dialog;

(function() {

	Dialog = Mask.extend({

		init: function(attrs) {
			this.attrs = attrs;

			this._super("body", attrs.text);

			this.width(attrs.width);
		},

		width: function(width) {
			if(!width) {
				return;
			}

			this.dom.find(".info").width(width);
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

			this.dom.addClass("dialog");

			var dialog = this.dom.find(".info");

			if(!this.attrs.waiting) {
				this.dom.find(".icon-spinner").hide();
			}

			var actions = $("<div class='actions' />");
			dialog.append(actions);

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
		}

	});

}());
