from django import forms

from parsr.models import Repo

class RepoForm(forms.ModelForm):

    class Meta:
        model = Repo
        fields = ["url", "kind", "timezone", "ignored_folders", "ignored_files", "anonymous", "user", "password"]

        def get_widget(widget, optional=False, autocomplete=True):
            attrs = {
                "class": "form-control"
            }

            if optional:
                attrs["class"] = "%s optional" % attrs["class"]

            if not autocomplete:
                attrs["autocomplete"] = "off"

            return widget(attrs=attrs)

        widgets = {
            "url": get_widget(forms.TextInput),
            "kind": get_widget(forms.Select),
            "timezone": get_widget(forms.Select),
            "ignored_folders": get_widget(forms.TextInput),
            "ignored_files": get_widget(forms.TextInput),
            "user": get_widget(forms.TextInput, "optional"),
            "password": get_widget(forms.PasswordInput, "optional")
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
