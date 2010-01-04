from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template import RequestContext

@login_required
def user_main(request):

    try:
        user = request.user.get_profile()
        subscriptions = user.subscription_set.all()
        mlists = [sub.mailing_list for sub in subscriptions]
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/usermain.html', {
            'user' : user,
            'subscriptions' : subscriptions,
            'mlists' : mlists,
            'groupstab' : True,
            }, context_instance = RequestContext(request))

@login_required
def user_profile(request):
    #implement this later when it's actually used.
    # it is currently unused.
    """
    """
    try:
        user = request.user.get_profile()
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/user-profile.html', {
            'user' : user,
            'profiletab' : True,
            }, context_instance = RequestContext(request))

@login_required
def user_password(request):

    """
    This view resets the user's password.
    """

    try:
        user = request.user.get_profile()
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/user-password.html', {
            'user' : user,
            'passwordtab' : True,
            }, context_instance = RequestContext(request))
