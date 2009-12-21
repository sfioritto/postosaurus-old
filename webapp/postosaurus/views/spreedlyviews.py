from django.contrib.auth.models import User
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


def update_subscriptions(request):

    """
    Receives a comma delimited list of user ids from spreedly. This view
    updates the users spreedly data for each id. Should probably dump
    this into a file and run a cron job once we actually have users...
    """

    ids = [int(id) for id in request.POST['subscriber_ids'].split(',')]
    print ids
    users = User.objects.filter(id__in=ids).all()
    print users
    for user in users:
        profile = user.get_profile()
        profile.update_from_spreedly()
    return render_to_response('postosaurus/plans.html', {
            }, context_instance = RequestContext(request))
