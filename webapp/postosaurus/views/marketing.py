from webapp import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from webapp.postosaurus.views import user
from lamson import view


def index(request):

    """
    If the user is not logged in they get the standard
    landing page. Otherwise they are redirected to the
    user's main view.
    """

    if request.user.is_anonymous():
        return render_to_response("postosaurus/home.html", 
                                  context_instance = RequestContext(request))

    else:
        return HttpResponseRedirect(reverse(user.main))
    

def plans(request):
    return render_to_response('postosaurus/plans.html', {
            'basic' : settings.SPREEDLY_PLAN_BASIC,
            }, context_instance = RequestContext(request))


def contact(request):
    return render_to_response('postosaurus/contact.html', 
                              context_instance = RequestContext(request))    

def faq(request):
    return render_to_response('postosaurus/faq.html', 
                              context_instance = RequestContext(request))


def about(request):
    return render_to_response('postosaurus/about.html', 
                              context_instance = RequestContext(request))

def privacy(request):
    return render_to_response('postosaurus/privacy.html', 
                              context_instance = RequestContext(request))

