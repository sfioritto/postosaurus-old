from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from app.model import mailinglist
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from webapp.postosaurus.models import *
from postosaurus.models import MailingList
import datetime

class ListNameField(forms.Field):
    def clean(self, list_name):
        """
        Postosaurus only accepts list names that have alphanumeric
        characters and a period.
        """
        if not list_name:
            raise forms.ValidationError('You must provide a name for your list.')
        
        if not mailinglist.valid_name(list_name):
            raise forms.ValidationError('List names are valid email addresses that contain letters, numbers and periods. e.g. awesome.list3')

        mlist = mailinglist.find_list(list_name)
        if mlist:
            raise forms.ValidationError('That list name has already been taken.')

        return list_name

class MailingListForm(forms.Form):
    email = forms.EmailField(max_length=512)
    name = ListNameField()

def index(request):
    return render_to_response("postosaurus/landing.html", {
            'form' : MailingListForm()
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

class SignupForm(forms.Form):
    email = forms.CharField(required=False)
    groupname = forms.CharField(required=False)
    links= forms.BooleanField(required=False)
    files = forms.BooleanField(required=False)
    tasks = forms.BooleanField(required=False)

def create_list(request):
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

def delete_subscription(request, subid):
    if request.method == 'POST':
        subscriber = Subscription.objects.get(pk=subid)
        mlist = subscriber.mailing_list
        mlistpage = "/app/lists/" + str(mlist.pk) + "/manage/"
        subscriber.delete()
        subscribers = mlist.subscription_set.all().order_by('-user').reverse()
        return HttpResponseRedirect(mlistpage)
        

def manage_list(request, listid):
    try:
        mlist = MailingList.objects.get(pk=listid)
        subscribers = mlist.subscription_set.all().order_by('-user').reverse()
    except ValueError:
        raise Http404()
    return render_to_response('postosaurus/manage.html', {
            'mlist': mlist,
            'subscribers': subscribers
            }, context_instance = RequestContext(request))

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


def links(request, listid, pagenum):
    try:
        mlist = MailingList.objects.get(pk=listid)
        links_list = mlist.link_set.all().order_by('-created_on')
        paginator = Paginator(links_list, 20) #sets links per page
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

def archive(request, listid):
    try:
        mlist = MailingList.objects.get(pk=listid)
        messages = mlist.message_set.all().order_by('-created_on')
    except ValueError:
        raise Http404()
    return render_to_response('postosaurus/archive.html', {
            'mlist': mlist,
            'messages': messages
            }, context_instance = RequestContext(request))

