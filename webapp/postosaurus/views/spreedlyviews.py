from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from webapp.forms import UserAccountForm

def __create_url(user, planid):
    puser = user.get_profile()
    return "https://spreedly.com/postosaurus/subscribers/%s/subscribe/%s/%s" % (str(user.id), planid, puser.email)


def plans(request):
    
    return render_to_response('postosaurus/plans.html', {
            }, context_instance = RequestContext(request))


def create_plan(request, planid):

    if request.user.is_anonymous():
        return render_to_response('postosaurus/create-user.html', {
                'form' : UserAccountForm(),
                'next' : request.path
                }, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(__create_url(request.user, planid))
