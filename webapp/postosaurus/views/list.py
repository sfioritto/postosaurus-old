from django.shortcuts import render_to_response
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from app.model import mailinglist, archive
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from webapp.postosaurus.models import *
from webapp.postosaurus.views import helpers
from email.utils import parseaddr  


#Django hack to let us put emails in the username field in the login form
AuthenticationForm.base_fields['username'].max_length = 75 


def authorize_or_raise(user, org):

    """
    Very simple authorization. This checks to see if the user is a member
    of the list and raises a permission denied error if they aren't.
    """

    if not user.in_org(org):
        raise PermissionDenied


@login_required
def members(request, listname):

    user = request.user.get_profile()
    mlist = mailinglist.find_list(listname)
    authorize_or_raise(user, mlist.organization)

    subscriptions = mlist.subscription_set.all()
    
    if request.method == 'POST':

        if not request.POST.has_key('confirmed'):
            # not confirmed yet.
            toremove = []
            for email in request.POST.keys():
                if request.POST[email]:
                    toremove.append(email)
            if len(toremove) > 0:
                return render_to_response('postosaurus/members-confirm.html', locals(), context_instance = RequestContext(request))

        # they confirmed, now remove the members.
        toremove = [key for key in request.POST.keys() if key != 'confirmed']
        for email in toremove:
            sub = mailinglist.find_subscription(email, listname)
            if sub:
                sub.delete()

        return render_to_response('postosaurus/members.html', {
                'mlist' : mlist,
                'subscriptions' : subscriptions,
                'membertab' : True,
                }, context_instance = RequestContext(request))

    else:
        return render_to_response('postosaurus/members.html', {
                'mlist' : mlist,
                'subscriptions' : subscriptions,
                'membertab' : True,
                }, context_instance = RequestContext(request))



@login_required
def archive_overview(request, listname):

    try:
        mlist = mailinglist.find_list(listname)
        user = request.user.get_profile()
        authorize_or_raise(user, mlist.organization)
        dbmessages = mlist.message_set.all().order_by('-created_on')
    except ValueError:
        raise Http404()
    
    messages = []
    for msg in dbmessages:
        month = msg.created_on.month
        day = msg.created_on.day
        year = msg.created_on.year
        url = reverse(archive_by_day, args=[listname, month, day, year])
        messages.append((msg, url))
    return render_to_response('postosaurus/archive.html', {
            'mlist': mlist,
            'messages': messages,
            'archivetab' : True,
            }, context_instance = RequestContext(request))


class CleanMessage(object):
    
    def __init__(self, message):

        """
        Takes json from the archive and turns
        it into clean json for the archive template.
        """
        
        if message['body']:
            self.body = message['body']
        else:
            self.body = message['parts'][0]['body']

        self.date = message['headers']['Date']
        name, email = parseaddr(message['headers']['From'])
        self.sender = name or email
        self.subject = message['headers']['Subject']


@login_required
def archive_by_day(request, listname, month, day, year):
    month = int(month)
    day = int(day)
    year = int(year)
    mlist = mailinglist.find_list(listname)
    user = request.user.get_profile()
    authorize_or_raise(user, mlist.organization)

    messages = [CleanMessage(msg) for msg in \
                    archive.messages_by_day(listname, year, month, day)]

    return render_to_response('postosaurus/archivebyday.html', {
            'mlist': mlist,
            'messages': messages,
            'date' : datetime(year, month, day),
            'archivetab' : True,
            }, context_instance = RequestContext(request))

    
