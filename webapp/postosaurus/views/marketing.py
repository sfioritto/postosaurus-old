from webapp import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site
from postosaurus.webapp.org.views import org, user
from webapp.forms import SignupForm, MailingListForm
from lamson import view

def index(request):

    """
    If the user is not logged in they get the standard
    landing page. Otherwise if there is a subdomain
    they go to that organizations main page. If there
    is no subdomain they simply go to the user main
    landing page.
    """

    django_site = Site.objects.get_current()
    if request.user.is_anonymous():
        return render_to_response("postosaurus/home.html", 
                                  context_instance = RequestContext(request))

    elif request.META['HTTP_HOST'] == django_site.domain:
        # The visitor has hit the main webpage, so redirect to /mypage/ 
        return HttpResponseRedirect(reverse(user.main))

    else:
        return org.main(request)
    

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

