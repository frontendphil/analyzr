var AddRepoForm;

(function() {

	AddRepoForm = Class.extend({
		init: function(target, toggle) {
			this.dom = $(target);

			this.toggle = $(toggle);

			var that = this;

			this.toggle.click(function() {
				that.update();
			});
		},

		getStatus: function() {
			return this.toggle.prop("checked");
		},

		update: function() {
			var el = this.dom.find(".optional").parents(".form-group");

			if(this.getStatus()) {
				el.slideUp();
			} else {
				el.slideDown();
			}
		}

	});

}());