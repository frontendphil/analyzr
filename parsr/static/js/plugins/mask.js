var Mask;

(function() {

	Mask = Class.extend({

		init: function(target, text) {
			this.container = $(target);
			this.text = text;

			this.render();
		},

		getMinHeight: function(container) {
			var value = container.css("minHeight");

			if(value === "0px") {
				return "100px";
			}

			return value;
		},

		getPosition: function(container) {
			var value = container.css("position");

			if(value === "static") {
				return "relative";
			}

			return value;
		},

		render: function() {
			var mask = $("<div class='mask' />");
			var info = $("<div class='info'><i class='icon-spinner icon-spin'></i> " + this.text + "</div>");

			mask.append(info);
			this.container.append(mask);

			this.container.css({
				"position": this.getPosition(this.container),
				"minHeight": this.getMinHeight(this.container)
			});

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
			this.dom.fadeOut(function() {
				$(this).remove();
			});
		},

		show: function() {
			if(!this.dom) {
				this.render();
			}

			this.dom.fadeIn();
		}

	});

}());
