import jinja2
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import check_password
from django.http import Http404
from django.template import RequestContext
from app.model import mailinglist
from webapp.forms import PasswordForm, MailingListForm

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
def user_main(request):

    try:
        profile = request.user.get_profile()
        subscriptions = profile.subscription_set.all()
        mlists = [sub.mailing_list for sub in subscriptions]
    except ValueError:
        raise Http404()
    
    form = MailingListForm()
    if request.method == "POST":
        form = MailingListForm(request.POST)
        
        # Let them know they need to pay up to create another list.
        if not profile.can_create_list():
            return render_to_response('postosaurus/usermain.html', {
                    'profile' : profile,
                    'subscriptions' : subscriptions,
                    'mlists' : mlists,
                    'groupstab' : True,
                    'form': form,
                    'payup' : True,
                    }, context_instance = RequestContext(request))
        
        #Check if the mailing list is valid.
        if form.is_valid():
            email = profile.email
            list_name = form.cleaned_data['groupname']
            mlist = mailinglist.create_list(list_name, profile)
            CONFIRM.send_if_not_subscriber(relay, mlist, 'confirm', email, 'postosaurus/join-confirmation.msg')

    return render_to_response('postosaurus/usermain.html', {
            'profile' : profile,
            'subscriptions' : subscriptions,
            'mlists' : mlists,
            'groupstab' : True,
            'form' : form,
            }, context_instance = RequestContext(request))

@login_required
def user_profile(request):
    # todo: implement this later when it's actually used.
    # it is currently unused.
    """
    """
    raise Http404()

@login_required
def user_password(request):

    """
    This view resets the user's password.
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
            return render_to_response('postosaurus/user-password.html', {
                    'form': form,
                    'passwordtab' : True,
                    'success' : changed,
                    }, context_instance = RequestContext(request))

    else:
        form = PasswordForm() # An unbound form

    
    return render_to_response('postosaurus/user-password.html', {
            'form' : form,
            'passwordtab' : True,
            'success' : changed,
            }, context_instance = RequestContext(request))


