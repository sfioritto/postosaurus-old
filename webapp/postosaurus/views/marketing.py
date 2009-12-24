import random
from django.shortcuts import render_to_response
from django.template import RequestContext
from webapp.postosaurus.models import BetaRequest
from webapp.forms import SignupForm, MailingListForm
from lamson import view


def index(request):
    return render_to_response("postosaurus/home.html", { 
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))


def plans(request):
    return render_to_response('postosaurus/plans.html', {
            }, context_instance = RequestContext(request))




