import os
import hashlib
from webapp import settings
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from pyspreedly import api


class User(models.Model):

    created_on = models.DateTimeField(auto_now_add=True, auto_now=True)
    email = models.CharField(max_length=512, primary_key=True)
    level = models.CharField(max_length=512, null=True) # the feature level from spreedly
    token = models.CharField(max_length=512, null=True) # the subscriber token from spreedly
    user = models.ForeignKey(DjangoUser, null=True)

    def is_subscribed(self, mlist):

        """
        Returns true or false to indicate if the user is subscribed
        to the given mailing list.
        """

        subs = mlist.subscription_set\
            .filter(user=self)\
            .filter(mailing_list=mlist)\
            .all()

        if len(subs) > 0:
            return True
        else:
            return False

    def update_from_spreedly(self):
        
        """
        Call this method to update application state based on the user's status
        in spreedly. If they aren't paying anymore, deactivate their lists.
        """

        client = api.Client(settings.SPREEDLY_TOKEN, settings.SPREEDLY_SITE)
        info = client.get_info(self.user.id)
        self.level = info['feature_level']  
        self.token = info['token']
        if info['active'] is False:
            for mlist in self.mailinglist_set.all():
                mlist.active = False
                mlist.save()
        self.save()

        
    def spreedly_account_url(self):
        return "https://spreedly.com/%s/subscriber_accounts/%s" % (settings.SPREEDLY_SITE, self.token)

    
    def tasks_requested(self):
        request = Request.objects.filter(email = self.email)
        if len(request) > 0:
            return True
        else:
            return False

    def __unicode__(self):
        return self.email
    

class Organization(models.Model):

    """
    Highest level of the models. Organizations have mailing lists,
    files, tasks (eventually), links, users. 
    """

    created_on = models.DateTimeField(auto_now_add=True, auto_now=True)
    name = models.CharField(max_length=63)
    owner = models.ForeignKey(User, null=True)
    active = models.BooleanField()
    
    def __unicode__(self):
        return self.name


class MailingList(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique = True)
    email = models.CharField(max_length=512, unique = True)
    organization = models.ForeignKey(Organization)
    
    def links_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.links', args=[self.name])


    def members_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.members', args=[self.name])


    def archive_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.archive_overview', args=[self.name])


    def __unicode__(self):
        return self.name


class Membership(models.Model):

    """
    Indicates a user is a member of an organization.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(User)


class Subscription(models.Model):

    """
    Indicates a user is subscribed to a mailing list.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    mailing_list = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return '%s' % (self.user.email)


class UserState(models.Model):

    """
    Stores state for Lamson.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=512)
    address = models.EmailField()
    state = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s:%s (%s)" % (self.key, self.address, self.state)


class JoinConfirmation(models.Model):
    address = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    secret = models.CharField(max_length=50)
    target = models.CharField(max_length=50)
    mlist = models.ForeignKey(MailingList)

    def __unicode__(self):
        return self.address


class Request(models.Model):

    """
    Feature request. Right now only used for tasks.
    Kill this model once tasks are implemented.
    """

    email = models.CharField(max_length=512)
    links = models.BooleanField()
    files = models.BooleanField()
    tasks = models.BooleanField()


class Message(models.Model):

    subject = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    mlist = models.ForeignKey(MailingList)

    def __unicode__(self):
        return str(self.id)

            
class Link(models.Model):

    message = models.ForeignKey(Message)
    mlist = models.ForeignKey(MailingList)
    url = models.CharField(max_length=2083)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.url

    def cleaned(self):
        return self.url
    

class File(models.Model):

    message = models.ForeignKey(Message)
    mlist = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)
    sha = models.CharField(max_length=40, unique = True)
    name = models.CharField(max_length=260)
    ext = models.CharField(max_length=260)
    created_on = models.DateTimeField(auto_now_add=True)


    def file_name_hash(self):
        return hashlib.sha1(self.name).hexdigest()
    

    def __get_url_prefix(self):

        """
        The relative path to the file. Tack
        on prefixes to get the url or path to
        the file in the filesystem.
        """
        path = os.path.join("/files/",
                            self.mlist.name[0], 
                            self.mlist.name, 
                            self.file_name_hash())
        return path

    urlprefix = property(__get_url_prefix)


    def __get_path_prefix(self):

        """
        The relative path to the file. Tack
        on prefixes to get the url or path to
        the file in the filesystem.
        """

        path = os.path.join(settings.FILES_DIR,
                            self.mlist.name[0], 
                            self.mlist.name, 
                            self.file_name_hash())
        return path
    pathprefix = property(__get_path_prefix)

    def local_path(self):

        """
        The local path to the file.
        """

        return os.path.join(self.pathprefix, self.sha, self.name)

    def url_path(self):
        """
        The files url.
        """
        return os.path.join(self.urlprefix, self.sha, self.name)

    def recent_local_path(self):
        """
        Every file has a most recent version. This is the
        path to that file.
        """

        return os.path.join(self.pathprefix, self.name)

    def recent_url_path(self):

        """
        Every file has a most recent version. This is the
        url to that file.
        """

        return os.path.join(self.urlprefix, self.name)

    def __unicode__(self):
        return self.name






