from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from app.model import mailinglist
from django.core.mail import send_mail
from django.template import Context, loader

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
            })

def create_list(request):
    if request.method == 'POST':
        form = MailingListForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            list_name = form.cleaned_data['name']
            mlist = mailinglist.create_list(list_name)
            user = mailinglist.create_user(email)
            add_if_not_subscriber(email, list_name)
            subject = 'Welcome to your first postosaurus group -- %s' % mlist.email
            t = loader.get_template('postosaurus/startemail.txt')
            c = Context({
                    'user' : user,
                    'mlist' : mlist
                    })

            body = t.render(c)
            send_mail(subject, body, mlist.email,
                      [user.email], fail_silently=False)

            return HttpResponseRedirect(reverse(list_created))
    else:
        form = MailingListForm() # An unbound form

    return render_to_response('postosaurus/landing.html', {
        'form': form,
    })


def list_created(request):
    return render_to_response('postosaurus/thanks.html')
