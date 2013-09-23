var Mask;

(function() {

	Mask = Class.extend({

		init: function(target, text) {
			this.container = $(target);
			this.text = text;

			this.render();
		},

		render: function() {
			var mask = $("<div class='mask' />");
			var info = $("<div class='info'>" + this.text + "</div>");

			mask.append(info);
			this.container.append(mask);

			this.dom = mask;

			this.layout();

			this.dom.hide();
		},

		layout: function() {
			var cHeight = this.container.height();
			var mHeight = this.dom.find(".info").height();

			this.dom.find(".info").css({
				marginTop: (cHeight / 2) - (mHeight / 2)
			});
		},

		remove: function() {
			this.dom.remove();
		},

		show: function() {
			if(!this.dom) {
				this.render();
			}

			this.dom.show();
		}

	});

}());