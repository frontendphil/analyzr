from hashlib import md5
from urllib import urlencode

from django import template
from django.db.models import Count

from parsr import utils
from parsr.models import Revision

register = template.Library()

class GravatarUrlNode(template.Node):
    def __init__(self, email):
        self.email = template.Variable(email)

    def render(self, context):
        try:
            email = self.email.resolve(context) or ""
        except template.VariableDoesNotExist:
            return ''

        size = 40

        mail = md5(email.lower()).hexdigest()
        params = urlencode({
            's': str(size)
        })

        return "<img src='http://www.gravatar.com/avatar/%s?%s' />" % (mail, params)


@register.filter
def is_checkbox(value):
	return value.field.__class__.__name__ == "BooleanField"


@register.filter
def href(value):
    return utils.href(value.__class__, value.id)


@register.tag
def gravatar(parser, token):
    try:
        tag_name, email = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return GravatarUrlNode(email)


@register.filter
def ranked(authors):
    return authors.annotate(revision_count=Count("revision")).order_by("-revision_count")


@register.filter
def rank(author, branch):
    return Revision.objects.filter(author=author, branch=branch).count()
