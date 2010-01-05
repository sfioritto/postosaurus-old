from app.model import mailinglist
from webapp.postosaurus.models import User
from django import forms
from django.contrib.auth.models import User as DjangoUser
from email.utils import parseaddr


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


class CustomEmailField(forms.EmailField):


    def clean(self, list_name):
        """
        Postosaurus only accepts list names that have alphanumeric
        characters and a period.
        """
        if not list_name:
            raise forms.ValidationError("You must enter your email address to create a group.")
        else:
            return forms.EmailField.clean(self, list_name)


class MailingListForm(forms.Form):

    groupname = ListNameField()


class SignupForm(forms.Form):
    
    email = forms.CharField(required=False)
    groupname = forms.CharField(required=False)
    links= forms.BooleanField(required=False)
    files = forms.BooleanField(required=False)
    tasks = forms.BooleanField(required=False)


class PasswordForm(forms.Form):
    
    oldpass = forms.CharField(label=(u'Your current password'),
                              widget=forms.PasswordInput(render_value=False))
    newpass = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False)) 
    verify = forms.CharField(label=(u'Password again'),
                               widget=forms.PasswordInput(render_value=False)) 

    def clean_newpass(self):
        if self.cleaned_data['newpass'] == self.data['verify']:
            return self.cleaned_data['newpass']
        else:
            raise forms.ValidationError("The passwords you entered in don't match.")


class UserAccountForm(forms.Form):

    email = forms.EmailField(max_length=75)
    username = forms.CharField(max_length=30)
    password = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False)) 
    repassword = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False)) 
    next = forms.CharField()


    def clean_password(self):
        if self.cleaned_data['password'] == self.data['repassword']:
            return self.cleaned_data['password']
        else:
            raise forms.ValidationError("The passwords you entered in don't match.")


    def clean_username(self):

        username = self.cleaned_data['username']

        try:
            duser = DjangoUser.objects.get(username=username)
        except DjangoUser.DoesNotExist:
            duser = None

        if duser:
            raise forms.ValidationError("This username is already taken.")
        else:
            return username

        
    def clean_email(self):

        email = self.cleaned_data['email']

        try:
            duser = DjangoUser.objects.get(email=email)
        except DjangoUser.DoesNotExist:
            duser = None

        try:
            user = User.objects.get(pk=email)
        except User.DoesNotExist:
            user = None

        if user or duser:
            raise forms.ValidationError("An account for this email address has already been created.")
        else:
            return email

            
        

        
