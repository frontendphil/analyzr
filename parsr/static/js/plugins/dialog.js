var Dialog;

(function() {

	Dialog = Mask.extend({

		init: function(attrs) {
			this.attrs = attrs;

			this._super("body", attrs.text);
		},

		standardButton: function() {
			var dismiss = $("<button class='btn btn-default'>Dismiss</button>");

			var that = this;

			dismiss.click(function() {
				that.remove();
			});

			this.dom.find(".info").append(dismiss);
		},

		render: function() {
			this._super();

			this.dom.addClass("dialog");

			if(!this.attrs.waiting) {
				this.dom.find(".icon-spinner").hide();
			}

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

				that.dom.find(".info").append(button);
			});
		}

	});

}());
