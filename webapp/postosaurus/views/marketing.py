import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from webapp.postosaurus.views import user_main
from webapp.postosaurus.models import BetaRequest
from webapp.forms import SignupForm, MailingListForm
from lamson import view



def index(request):
    if request.user.is_anonymous():
        return render_to_response("postosaurus/home.html", { 
                'form' : MailingListForm(),
                }, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse(user_main))


def plans(request):
    return render_to_response('postosaurus/plans.html', {
            'basic' : settings.SPREEDLY_PLAN_BASIC,
            }, context_instance = RequestContext(request))

def landing_contact(request):
    return render_to_response('postosaurus/landing-contact.html', 
                              context_instance = RequestContext(request))    

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

