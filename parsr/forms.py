from django import forms

from parsr.models import Repo

class RepoForm(forms.ModelForm):

	class Meta:
		model = Repo
		fields = ["url", "kind", "timezone", "anonymous", "user", "password"]

		def get_widget(widget, cls=""):
			return widget(attrs={"class": "form-control %s" % cls})

		widgets = {
			"url": get_widget(forms.TextInput),
			"kind": get_widget(forms.Select),
			"timezone": get_widget(forms.Select),
			"user": get_widget(forms.TextInput, "optional"),
			"password": get_widget(forms.TextInput, "optional")
		}

	def is_valid(self):
		valid = super(RepoForm, self).is_valid()

		if not valid:
			return False

		if not self["anonymous"].value():
			if not self["user"].value():
				valid = False

				self.errors["user"] = True

			if not self["password"].value():
				valid = False

				self.errors["password"] = True

			return valid

		return True
