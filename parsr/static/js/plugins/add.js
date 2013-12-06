ns("plugins");

(function() {

	analyzr.plugins.AddRepoForm = analyzr.core.Class.extend({
		init: function(target, toggle) {
			this.form = $(target);

			this.toggle = $(toggle);

			var that = this;

			this.toggle.click(function() {
				that.update();
			});

			this.form.find("input").each(function() {
				$(this).attr("autocomplete", "off");
			});

			this.form.on("submit", function(e) {
				return that.handleSubmit(e);
			});
		},

		getData: function() {
			var data = {};

			var gather = function() {
				var name = $(this).attr("name");
				var value;

				if($(this).attr("type") === "checkbox") {
					value = $(this).prop("checked");
				} else {
					value = $(this).prop("value");
				}

				data[name] = value;
			};

			this.form.find("input").each(gather);
			this.form.find("select").each(gather);

			return data;
		},

		handleSubmit: function(event) {
			event.preventDefault();

			var that = this;
			var mask = new analyzr.core.Mask("body", "Creating repository. Please wait...");

			$.ajax(this.form.attr("action"), {
				method: "POST",
				data: this.getData(),
				beforeSend: function() {
					mask.show();
				},
				success: function() {
					window.location.href = "/";
				},
				error: function(data) {
					that.form.find(".form-group").removeClass("has-error");

					$.each(data.responseJSON, function(key) {
						that.form.find("*[name=" + key + "]").parents(".form-group").addClass("has-error");
					});

					mask.remove();

					if(data.responseJSON.repo) {
						var dialog = new analyzr.plugins.Dialog("There seems to be an error with the repo properties. Please check the URL, kind, and the credentials.");
						dialog.show();
					}
				}
			})

			return false;
		},

		getStatus: function() {
			return this.toggle.prop("checked");
		},

		update: function() {
			var el = this.form.find(".optional").parents(".form-group");

			if(this.getStatus()) {
				el.slideUp();
			} else {
				el.slideDown();
			}
		}

	});

}());
