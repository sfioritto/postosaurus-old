from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import check_password, User as DjangoUser
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from app.model import mailinglist
from webapp.postosaurus.views import helpers
from webapp.postosaurus import models
from webapp.forms import PasswordForm, UserAccountForm




@login_required
def settings(request):

    """
    This view resets the user's password. Eventually
    a user can do more, but this is it for now.
    """

    try:
        profile = request.user.get_profile()
    except ValueError:
        raise Http404()

    changed = False
    profile.update_from_spreedly()
    if request.method == 'POST':

        form = PasswordForm(request.POST)
        user = request.user
        
        # Check if the new password is valid and if the old password matches.
        if form.is_valid() and check_password(form.cleaned_data['oldpass'], user.password):
            newpassword = form.cleaned_data['newpass']
            user.set_password(newpassword)
            user.save()
            changed = True
            
    else:
        form = PasswordForm() # An unbound form

    return render_to_response('postosaurus/user-settings.html', {
            'profile' : profile,
            'form' : form,
            'settingstab' : True,
            'success' : changed,
            }, context_instance = RequestContext(request))


def create_user(request):
    
    """
    Creates an account for the web application.
    """

    next = "/"
    form = UserAccountForm()
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        next = form.data['next']
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            repassword = form.cleaned_data['repassword']
            email = form.cleaned_data['email']

            djangouser, user = helpers.create_users(username, email, password)
            
            djangouser = authenticate(username=djangouser.username, password=password)
            login(request, djangouser)

            return HttpResponseRedirect(next)

    else:

        # override next if there is a value in the query string.
        if request.GET.has_key('next'):
            if request.GET['next']:
                next = request.GET['next']

    return render_to_response('postosaurus/create-user.html', {
            'form' : form,
            'next' : next
            }, context_instance = RequestContext(request))


