from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import check_password
from django.http import Http404
from django.template import RequestContext
from webapp.forms import PasswordForm

@login_required
def user_main(request):

    try:
        puser = request.user.get_profile()
        subscriptions = puser.subscription_set.all()
        mlists = [sub.mailing_list for sub in subscriptions]
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/usermain.html', {
            'puser' : puser,
            'subscriptions' : subscriptions,
            'mlists' : mlists,
            'groupstab' : True,
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


