from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from webapp.forms import UserAccountForm
from webapp.postosaurus.views import create_user

def __create_url(user, planid):
    puser = user.get_profile()
    return "https://spreedly.com/postosaurus/subscribers/%s/subscribe/%s/%s" % (str(user.id), planid, puser.email)


def plans(request):
    return render_to_response('postosaurus/plans.html', {
            }, context_instance = RequestContext(request))

def create_subscription(request, planid):

    """
    Call the create_user view. Make sure that this view is executed once the form has
    been successfully processed by setting the next variable. Also, set a custom template.

    Once the view has been completed, the user will be logged in and redirected to this view.
    This view then redirects them to spreedly.
    """

    if request.user.is_anonymous():
        return create_user(request, template='postosaurus/create-subscription.html', next=request.path)
    else:
        return HttpResponseRedirect(__create_url(request.user, planid))

