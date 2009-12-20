import random
from django.shortcuts import render_to_response
from django.template import RequestContext
from webapp.postosaurus.models import BetaRequest
from webapp.forms import SignupForm, MailingListForm
from lamson import view

def index(request):
    return render_to_response("landing/signup.html", { 
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))


def signup(request):
    #Remove after changing index
    return render_to_response("landing/signup.html", {
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))
 

def landing(request):
    number = str(random.randint(1, 2))
    url = "landing/landing" + number + ".html/"
    return render_to_response(url, {
            }, context_instance = RequestContext(request))

def out_of_space(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            betaRequest = BetaRequest(email=email)
            betaRequest.save()
    return render_to_response('landing/thanks.html')
