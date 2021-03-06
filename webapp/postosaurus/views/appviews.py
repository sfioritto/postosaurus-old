from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from app.model import mailinglist, archive
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import login, authenticate
from webapp.postosaurus.models import *
from webapp.forms import MailingListForm, UserAccountForm
from email.utils import parseaddr  
import webapp.settings as settings

#Django hack to let us put emails in the username field in the login form
AuthenticationForm.base_fields['username'].max_length = 75 
 

def create_user(request, template='postosaurus/create-user.html', next=settings.LOGIN_URL):
    
    """
    Creates an account for the web application.
    """

    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        next = form.data['next']
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            repassword = form.cleaned_data['repassword']
            email = form.cleaned_data['email']

            #never populate the email address of the django model. This is duplicated
            #in the postosaurus user model.
            djangouser = DjangoUser.objects.create_user(username, '', password)
            djangouser.save()
            user = mailinglist.find_user(email)
            if not user:
                user = User(email=email)
                user.save()

            user.user = djangouser
            user.save()
            
            djangouser = authenticate(username=djangouser.username, password=password)
            login(request, djangouser)

            return HttpResponseRedirect(next)
        else:
            return render_to_response(template, {
                    'form' : form,
                    'next' : next
                    }, context_instance = RequestContext(request))
    else:

        # override next if there is a value in the query string.
        if request.GET.has_key('next'):
            if request.GET['next']:
                next = request.GET['next']

        return render_to_response(template, {
                'form' : UserAccountForm(),
                'next' : next
                }, context_instance = RequestContext(request))


def _authorize_or_raise(user, mlist):

    """
    Very simple authorization. This checks to see if the user is a member
    of the list and raises a permission denied error if they aren't.
    """

    if not user.is_subscribed(mlist):
        raise PermissionDenied


@login_required
def members(request, listname):

    user = request.user.get_profile()
    mlist = mailinglist.find_list(listname)
    _authorize_or_raise(user, mlist)

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
def links(request, listname):

    try:
        user = request.user.get_profile()
        mlist = mailinglist.find_list(listname)
        _authorize_or_raise(user, mlist)
        alllinks = mlist.link_set.all().order_by('-created_on')
        paginator = Paginator(alllinks, 15) #sets links per page

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            links = paginator.page(page)
        except (EmptyPage, InvalidPage):
            links = paginator.page(paginator.num_pages)
            
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/links.html', {
            'mlist': mlist, 
            'links': links,
            'linktab' : True,
            }, context_instance = RequestContext(request))


@login_required
def tasks(request, listname):

    try:
        profile = request.user.get_profile()
        mlist = mailinglist.find_list(listname)
        _authorize_or_raise(profile, mlist)
            
    except ValueError:
        raise Http404()

    if request.method == 'POST':
        feature = Request(email=profile.email,
                          links=False,
                          files=False,
                          tasks=True)
        feature.save()

    return render_to_response('postosaurus/tasks.html', {
            'profile' : profile,
            'mlist': mlist, 
            'taskstab' : True,
            }, context_instance = RequestContext(request))


@login_required
def files(request, listname):

    user = request.user.get_profile()
    mlist = mailinglist.find_list(listname)
    _authorize_or_raise(user, mlist)
    files = mlist.file_set.all().order_by('-created_on')

    paginator = Paginator(files, 15) #sets links per page

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        files = paginator.page(page)
    except (EmptyPage, InvalidPage):
        files = paginator.page(paginator.num_pages)
    
    return render_to_response('postosaurus/files.html', {
            'mlist': mlist, 
            'files': files,
            'filetab' : True,
            }, context_instance = RequestContext(request))


@login_required
def archive_overview(request, listname):

    try:
        mlist = mailinglist.find_list(listname)
        user = request.user.get_profile()
        _authorize_or_raise(user, mlist)
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
    _authorize_or_raise(user, mlist)

    messages = [CleanMessage(msg) for msg in \
                    archive.messages_by_day(listname, year, month, day)]

    return render_to_response('postosaurus/archivebyday.html', {
            'mlist': mlist,
            'messages': messages,
            'date' : datetime(year, month, day),
            'archivetab' : True,
            }, context_instance = RequestContext(request))

    
