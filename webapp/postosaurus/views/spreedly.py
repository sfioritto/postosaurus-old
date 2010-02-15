from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from webapp.postosaurus.views import helpers
from webapp.forms import OrgUserForm
from webapp.postosaurus import models
from webapp import settings


def __create_url(user, planid):
    puser = user.get_profile()
    return "https://spreedly.com/%s/subscribers/%s/subscribe/%s/%s" % (settings.SPREEDLY_SITE, str(user.id), planid, puser.email)


def create_subscription(request, planid):

    """
    Creates an organization and a user.

    Once the view has been completed, the user will be logged in and redirected to this view.
    This view then redirects them to spreedly.
    """


    if request.user.is_anonymous():
        form = OrgUserForm()
        if request.method == 'POST':

            form = OrgUserForm(request.POST)
            if form.is_valid():

                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                repassword = form.cleaned_data['repassword']
                email = form.cleaned_data['email']
                subdomain = form.cleaned_data['subdomain']
                orgname = form.cleaned_data['orgname']
                
                djangouser, user = helpers.create_users(username, email, password)
                
                org = models.Organization(subdomain = subdomain,
                                          name = orgname,
                                          owner = user,
                                          active = False) # becomes active once they enter payment info.
                org.save()
                
                membership = models.Membership(organization = org,
                                               user = user)
                membership.save()
                
                djangouser = authenticate(username=djangouser.username, password=password)
                login(request, djangouser)
                
                return HttpResponseRedirect(__create_url(djangouser, planid))
            
        return render_to_response('postosaurus/create-subscription.html', {
                'form' : form,
                'next' : next
                }, context_instance = RequestContext(request))
        
    else:
        return HttpResponseRedirect(__create_url(request.user, planid))
            
                    
def update_subscriptions(request):

    """
    Receives a comma delimited list of user ids from spreedly. This view
    updates the users spreedly data for each id. Should probably dump
    this into a file and run a cron job once we actually have users...
    """

    ids = [int(id) for id in request.POST['subscriber_ids'].split(',')]
    users = models.User.objects.filter(id__in=ids).all()
    for user in users:
        profile = user.get_profile()
        profile.update_from_spreedly()
    return render_to_response('postosaurus/plans.html', {
            }, context_instance = RequestContext(request))


@login_required
def billing(request):

    try:
        profile = request.user.get_profile()
    except ValueError:
        raise Http404()

    url, plans = None, None
    if profile.token:
        url = profile.spreedly_account_url()
    else:
        plans = __create_url(request.user, settings.SPREEDLY_PLAN_BASIC)
    return render_to_response('postosaurus/user-billing.html', {
            'profile' : profile,
            'url' : url,
            'plans' : plans,
            'billingtab' : True,
            }, context_instance = RequestContext(request))
