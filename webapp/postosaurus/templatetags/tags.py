from django import template
from django.core.urlresolvers import reverse
from webapp import settings
from webapp.postosaurus.views.list import members

register = template.Library()


@register.tag
def org_url(parser, token):

    """
    Creates an OrgUrlNode which is used to render
    urls for organizations, which are different in production
    versus 
    """

    try:
        nodes = token.split_contents()
        assert len(nodes) > 1
        tagname, viewname = nodes[0], nodes[1]
    except:
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % token.contents.split()[0]

    args = [template.Variable(node.strip(",")) for node in nodes[2:]]
    return OrgUrlNode(viewname, args)


class OrgUrlNode(template.Node):

    def __init__(self, viewname, args):
        self.viewname = viewname
        self.args = args

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        url = reverse('webapp.postosaurus.views.list.members', args=args)
        if settings.DEBUG:
            return url
        else:
            return url


