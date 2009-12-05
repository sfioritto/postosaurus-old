import os
import hashlib
from webapp import settings
from django.db import models
from datetime import datetime
from email.utils import formataddr
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse


class User(models.Model):


    created_on = models.DateTimeField(auto_now_add=True, auto_now=True)
    email = models.CharField(max_length=512, primary_key=True)
    user = models.ForeignKey(DjangoUser, null=True)

    def is_subscribed(self, mlist):

        subs = mlist.subscription_set\
            .filter(user=self)\
            .filter(mailing_list=mlist)\
            .all()

        if len(subs) > 0:
            return True
        else:
            return False


    def __unicode__(self):
        return self.email


class MailingList(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique = True)
    email = models.CharField(max_length=512, unique = True)

    
    def links_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.links', args=[self.name])


    def members_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.members', args=[self.name])


    def archive_url(self):
        return "http://www.postosaurus.com" + reverse('webapp.postosaurus.views.archive_overview', args=[self.name])


    
    def __unicode__(self):
        return self.name


class Subscription(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    mailing_list = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return '%s' % (self.user.email)


class UserState(models.Model):
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
    email = models.CharField(max_length=512)
    links = models.BooleanField()
    files = models.BooleanField()
    tasks = models.BooleanField()


class BetaRequest(models.Model):
    email = models.CharField(max_length=512)


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






