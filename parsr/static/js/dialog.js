var Dialog;

(function() {

	Dialog = Mask.extend({

		init: function(text) {
			this._super("body", text);
		},

		render: function() {
			this._super();

			this.dom.addClass("dialog");

			var dismiss = $("<button class='btn btn-default'>Dismiss</button>");

			var that = this;

			dismiss.click(function() {
				that.remove();
			});

			this.dom.find(".info").append(dismiss);
		}

	});

}());