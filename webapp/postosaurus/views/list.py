import jinja2
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from app.model import mailinglist, archive, files as appfiles
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from webapp.postosaurus.models import *
from webapp.postosaurus.views import helpers
from email.utils import parseaddr  
from webapp import settings, forms
from lamson import view

# relay is created at runtime in boot.py for lamson, but django
# doesn't know about it, so I create it here. Might be better
# to just use built in django email stuff instead of lamson?
# this code is duplicated in org views.
from config import settings as appsettings
from lamson.server import Relay
appsettings.relay = Relay(host=appsettings.relay_config['host'], 
                       port=appsettings.relay_config['port'], debug=1)

#same thing here for the loader.
view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(appsettings.template_config['dir'], 
                                appsettings.template_config['module']))

from config.settings import relay, CONFIRM


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
def file_versions(request, orgname, listname, filename):
    try:
        profile = request.user.get_profile()
        mlist = mailinglist.find_list(listname, orgname)
        org = mlist.organization
        dbfiles = File.objects\
            .filter(organization=org)\
            .filter(mlist=mlist)\
            .filter(name=filename).all()
    except ValueError:
        raise Http404()

    if len(dbfiles) == 0:
        raise Http404()

    return render_to_response('postosaurus/file-versions.html', {
            'org' : mlist.organization,
            'mlist' : mlist,
            'files' : dbfiles,
            'filestab' : True,
            'filename' : filename,
            'form' : forms.UploadFileForm(),
            }, context_instance = RequestContext(request))


@login_required
def upload_file(request, orgname, listname):

    try:
        profile = request.user.get_profile()
        mlist = mailinglist.find_list(listname, orgname)
    except ValueError:
        raise Http404()
    
    if request.method == "POST":
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            appfiles.store_file(profile, mlist, mlist.organization, request.FILES['file'])
        return HttpResponseRedirect(request.POST['next'])
    else:
        raise Http404()

@login_required
def files(request, orgname, listname):

    try:
        profile = request.user.get_profile()
        mlist = mailinglist.find_list(listname, orgname)
        dbfiles = mlist.file_set.all().order_by('-created_on')
    except ValueError:
        raise Http404()
    files = {}
    for f in dbfiles:
        files[f.name] = f

    return render_to_response('postosaurus/files.html', {
            'org' : mlist.organization,
            'mlist' : mlist,
            'files' : files.values(),
            'filestab' : True,
            'form' : forms.UploadFileForm(),
            }, context_instance = RequestContext(request))


@login_required
def invite_member(request, orgname, listname):

    try:
        mlist = mailinglist.find_list(listname, orgname)
        org = mlist.organization
    except ValueError:
        raise Http404()

    if request.method == "POST":

        email = request.POST['email']
        CONFIRM.send_if_not_subscriber(relay, 
                                       mlist, 
                                       'confirm', 
                                       email, 
                                       'postosaurus/join-confirmation.msg',
                                       org.subdomain + '.' + settings.HOST)

        return render_to_response('postosaurus/invite-sent.html', {
                'org' : org,
                'mlist' : mlist,
                'email' : email,
                'membertab' : True,
                }, context_instance = RequestContext(request))
    

    else:
        return render_to_response('postosaurus/invite-members.html', {
                'org' : org,
                'mlist' : mlist,
                'membertab' : True,
                }, context_instance = RequestContext(request))


@login_required
def edit_members(request, orgname, listname):

    try:
        user = request.user.get_profile()
        mlist = mailinglist.find_list(listname, orgname)
        subscriptions = mlist.subscription_set.all()
    except ValueError:
        raise Http404()

    if request.method == "POST":

        emails = helpers.emails_from_post(request.POST)

        if request.POST.has_key("confirmed"):
            for email in emails:
                helpers.remove_from_list(email, mlist, mlist.organization)
        else:
            return render_to_response('postosaurus/members-confirm.html', {
                    'org' : mlist.organization,
                    'mlist' : mlist,
                    'emails' : emails,
                    }, context_instance = RequestContext(request))

    return render_to_response('postosaurus/edit-members.html', {
            'org' : mlist.organization,
            'mlist' : mlist,
            'subscriptions' : subscriptions,
            'membertab' : True,
            }, context_instance = RequestContext(request))
    
    
    
@login_required
def members(request, orgname, listname):


    try:
        user = request.user.get_profile()
        mlist = mailinglist.find_list(listname, orgname)
        subscriptions = mlist.subscription_set.all()
        pending = mlist.joinconfirmation_set.all()
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/members.html', {
            'org' : mlist.organization,
            'mlist' : mlist,
            'subscriptions' : subscriptions,
            'pending' : pending,
            'membertab' : True,
            }, context_instance = RequestContext(request))



@login_required
def archive_overview(request, orgname, listname):

    try:
        mlist = mailinglist.find_list(listname, orgname)
        profile = request.user.get_profile()
        dbmessages = mlist.message_set.all().order_by('-created_on')
    except ValueError:
        raise Http404()
    
    messages = []
    for msg in dbmessages:
        month = msg.created_on.month
        day = msg.created_on.day
        year = msg.created_on.year
        url = reverse(archive_by_day, args=[orgname, listname, month, day, year])
        messages.append((msg, url))
    return render_to_response('postosaurus/archive.html', {
            'org' : mlist.organization,
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
def archive_by_day(request, orgname, listname, month, day, year):
    month = int(month)
    day = int(day)
    year = int(year)
    mlist = mailinglist.find_list(listname)
    user = request.user.get_profile()

    messages = [CleanMessage(msg) for msg in \
                    archive.messages_by_day(mlist, year, month, day)]

    return render_to_response('postosaurus/archivebyday.html', {
            'mlist': mlist,
            'messages': messages,
            'date' : datetime(year, month, day),
            'archivetab' : True,
            }, context_instance = RequestContext(request))

    
