import jinja2
from webapp.postosaurus.views.list import authorize_or_raise
from django.shortcuts import render_to_response
from django.http import Http404
from app.model import mailinglist
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from webapp.postosaurus.models import *
from webapp.forms import MailingListForm
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
def main(request, orgname):
    try:
        profile = request.user.get_profile()
        organization = Organization.objects.get(subdomain=orgname)
        mlists = organization.mailinglist_set.all()
    except ValueError:
        raise Http404()
    
    form = MailingListForm()
    mlist = None
    if request.method == "POST":
        form = MailingListForm(request.POST)
        
        #Check if the mailing list is valid.
        if form.is_valid():
            email = profile.email
            list_name = form.cleaned_data['groupname']
            mlist = mailinglist.create_list(list_name, organization)
            CONFIRM.send_if_not_subscriber(relay, mlist, 
                                           'confirm', email, 
                                           'postosaurus/join-confirmation.msg')
            
    return render_to_response('postosaurus/org-lists.html', {
            'org' : organization,
            'mlist' : mlist,
            'mlists' : mlists,
            'groupstab' : True,
            'form' : form,
            }, context_instance = RequestContext(request))


@login_required
def members(request, orgname):
    return main(request, orgname)


@login_required
def links(request, orgname):

    try:
        user = request.user.get_profile()
        mlist = mailinglist.find_list(listname)
        authorize_or_raise(user, mlist)
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
def tasks(request, orgname):

    try:
        profile = request.user.get_profile()
        mlist = mailinglist.find_list(listname)
        authorize_or_raise(profile, mlist)
            
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
def files(request, orgname):

    user = request.user.get_profile()
    mlist = mailinglist.find_list(listname)
    authorize_or_raise(user, mlist)
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
