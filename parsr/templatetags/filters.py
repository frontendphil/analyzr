from django import template

register = template.Library()

@register.filter
def is_checkbox(value):
	return value.field.__class__.__name__ == "BooleanField"
