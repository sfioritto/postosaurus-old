import jinja2
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import check_password
from django.http import Http404
from django.template import RequestContext
from webapp.postosaurus import models
from webapp.forms import PasswordForm
from lamson import view

# relay is created at runtime in boot.py for lamson, but django
# doesn't know about it, so I create it here. Might be better
# to just use built in django email stuff instead of lamson?
from config import settings as appsettings
from lamson.server import Relay
appsettings.relay = Relay(host=appsettings.relay_config['host'], 
                       port=appsettings.relay_config['port'], debug=1)

#same thing here for the loader.
view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(appsettings.template_config['dir'], 
                                appsettings.template_config['module']))


from config.settings import relay, CONFIRM


@login_required
def main(request):

    """
    For now just shows user setgings.
    TODO: Returns a list of the users organizations
    """
    return settings(request)


@login_required
def settings(request):

    """
    This view resets the user's password. Eventually
    a user can do more, but this is it for now.
    """

    changed = False

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

    
    return render_to_response('postosaurus/user-password.html', {
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

            djangouser, user = models.create_users(email, username, password)
            
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
