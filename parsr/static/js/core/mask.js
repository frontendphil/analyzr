ns("core");

(function() {

	analyzr.core.Mask = analyzr.core.Observeable.extend({

		init: function(target, text) {
			this._super();

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
			var body = $(
				"<div class='body'>" +
					"<div class='content'>" +
						"<i class='icon-spinner icon-spin'></i> " +
						"<span class='text'>" + this.text + "</span>" +
					"</div>" +
				"</div>"
			);

			mask.append(body);
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
			var cHeight = Math.min(this.container.height(), window.innerHeight);
			var mHeight = this.dom.find(".body").height();

			this.dom.find(".body").css({
				marginTop: window.scrollY + (cHeight / 2) - (mHeight / 2)
			});

			this.raise("layout");
		},

		remove: function() {
			var that = this;

			this.dom.fadeOut(function() {
				$(this).remove();
				that.container.css({
					"minHeight": ""
				});
			});
		},

		show: function() {
			if(!this.dom) {
				this.render();
			}

			var that = this;

			// focus this element
			that.dom.click();

			this.dom.fadeIn(function() {
				that.raise("show");
			});
		}

	});

}());
