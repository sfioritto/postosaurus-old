import random
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from app.model import mailinglist, archive
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import login, authenticate
from webapp.postosaurus.models import *

from webapp.forms import SignupForm, MailingListForm, UserAccountForm
from email.utils import parseaddr  
import webapp.settings as settings

AuthenticationForm.base_fields['username'].max_length = 75 


def index(request):
    return render_to_response("postosaurus/signup.html", { 
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))


def signup(request):
    #Remove after changing index
    return render_to_response("postosaurus/signup.html", {
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))
 
def landing(request):
    number = str(random.randint(1, 2))
    url = "postosaurus/landing" + number + ".html/"
    return render_to_response(url, {
            }, context_instance = RequestContext(request))
 

# def create_list(request):
#     if request.method == 'POST':
#         form = MailingListForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             list_name = form.cleaned_data['name']
#             mlist = mailinglist.create_list(list_name)
#             user = mailinglist.create_user(email)
#             mailinglist.add_if_not_subscriber(email, list_name)
#             subject = 'Welcome to your first postosaurus group -- %s' % mlist.email
#             t = loader.get_template('postosaurus/startemail.txt')
#             c = Context({
#                     'user' : user,
#                     'mlist' : mlist
#                     })

#             body = t.render(c)
#             send_mail(subject, body, mlist.email,
#                       [user.email], fail_silently=False)

#             return HttpResponseRedirect(reverse(list_created))
#     else:
#         form = MailingListForm() # An unbound form

#     return render_to_response('postosaurus/landing.html', {
#         'form': form,
#     }, context_instance = RequestContext(request))


def create_list(request):
    if request.method =='GET':
        return render_to_response("postosaurus/signup.html", {
            'form' : MailingListForm(),
            }, context_instance = RequestContext(request))
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            links = form.cleaned_data['links']
            files = form.cleaned_data['files']
            tasks = form.cleaned_data['tasks']
            aRequest = Request(email=email, links=links, files=files, tasks=tasks)
            aRequest.save()
            return render_to_response('postosaurus/beta.html', {
                    'form' : form,
                    }, context_instance = RequestContext(request))
    return render_to_response('postosaurus/landing.html')


def create_user(request):
    
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

            djangouser = DjangoUser.objects.create_user(username, email, password)
            user = mailinglist.find_user(email)
            if not user:
                user = User(email=email)
                user.save()

            user.djangouser = djangouser
            user.save()
            
            djangouser = authenticate(username=djangouser.username, password=password)
            login(request, djangouser)

            return HttpResponseRedirect(next)
        else:
            print form.errors
            return render_to_response('postosaurus/create-user.html', {
                    'form' : form,
                    'next' : next
                    }, context_instance = RequestContext(request))
    else:
        next = settings.LOGIN_URL

        # override next if there is a value in the query string.
        if request.GET.has_key('next'):
            next = request.GET['next']

        return render_to_response('postosaurus/create-user.html', {
                'form' : UserAccountForm(),
                'next' : next
                }, context_instance = RequestContext(request))


@login_required
def members(request, listname):
    mlist = mailinglist.find_list(listname)
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

        return render_to_response('postosaurus/members.html', locals(), context_instance = RequestContext(request))

    else:
        return render_to_response('postosaurus/members.html', locals(), context_instance = RequestContext(request))


def out_of_space(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            betaRequest = BetaRequest(email=email)
            betaRequest.save()
    return render_to_response('postosaurus/thanks.html')


def list_created(request):
    return render_to_response('postosaurus/thanks.html', context_instance = RequestContext(request))


@login_required
def links(request, listname):

    try:
        mlist = mailinglist.find_list(listname)
        alllinks = mlist.link_set.all().order_by('-created_on')
        paginator = Paginator(alllinks, 20) #sets links per page

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
            'links': links
            }, context_instance = RequestContext(request))

@login_required
def archive_overview(request, listname):

    try:
        mlist = mailinglist.find_list(listname)
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
            'messages': messages
            }, context_instance = RequestContext(request))


class CleanMessage(object):
    
    def __init__(self, message):

        """
        Takes json from the archive and turns
        it into lean json for the archive template.
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
    messages = [CleanMessage(msg) for msg in \
                    archive.messages_by_day(listname, year, month, day)]

    return render_to_response('postosaurus/archivebyday.html', {
            'mlist': mlist,
            'messages': messages,
            'date' : datetime(year, month, day),
            }, context_instance = RequestContext(request))


@login_required
def user_main(request, useremail):

    try:
        user = User.objects.get(pk=useremail)
        subscriptions = user.subscription_set.all()
    except ValueError:
        raise Http404()

    return render_to_response('postosaurus/usermain.html', locals(), context_instance = RequestContext(request))

def page_not_found(request):
    #Handles 404 errors
    return render_to_response('postosaurus/404.html', context_instance = RequestContext(request))

def server_error(request):
    #Handles 500 errors
    return render_to_response('postosaurus/500.html', context_instance = RequestContext(request))

