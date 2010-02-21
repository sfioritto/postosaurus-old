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


    def in_org(self, org):

        """
        Returns true or false to indicate if the user is in
        to the given organization.
        """

        memberships = mlist.membership_set\
            .filter(user=self)\
            .filter(organization=org)\
            .all()

        if len(memberships) > 0:
            return True
        else:
            return False

    def billing_active(self):
        
        #if not in production, all billing plans are active.
        if settings.DEBUG:
            return True

        client = api.Client(settings.SPREEDLY_TOKEN, settings.SPREEDLY_SITE)
        try:
            info = client.get_info(self.user.id)
            return info['active']
        except:
            return False

    def update_from_spreedly(self):
        
        """
        Call this method to update application state based on the user's status
        in spreedly. If they aren't paying anymore, deactivate their lists.
        """

        #only do this in production.
        if not settings.DEBUG:
            client = api.Client(settings.SPREEDLY_TOKEN, settings.SPREEDLY_SITE)
            try:
                info = client.get_info(self.user.id)
                self.level = info['feature_level']  
                self.token = info['token']
                if info['active'] is False:
                    for org in self.organization_set.all():
                        org.active = False
                        org.save()
                else:
                    for org in self.organization_set.all():
                        if not org.active:
                            org.active = True
                            org.save()
                self.save()
            except:
                #todo: I should probably log here.
                pass

        
    def spreedly_account_url(self):
        return "https://spreedly.com/%s/subscriber_accounts/%s" % (settings.SPREEDLY_SITE, self.token)

    

    def __url(self):
        return reverse('webapp.postosaurus.views.user.settings')
    url = property(__url)

    def __unicode__(self):
        return self.email
    

class Organization(models.Model):

    """
    Highest level of the models. Organizations have mailing lists,
    files, users. 
    """

    created_on = models.DateTimeField(auto_now_add=True, auto_now=True)
    subdomain = models.CharField(max_length=63, unique=True)
    name = models.CharField(max_length=300)
    owner = models.ForeignKey(User, null=True)
    active = models.BooleanField()
    
    
    def __url(self):
        if settings.URL_DEBUG:
            return reverse('webapp.postosaurus.views.org.main', 
                           args=[self.subdomain])
        else:
            return "www.%s.postosaurus.com" % self.subdomain
    url = property(__url)


    def __membersurl(self):
        if settings.URL_DEBUG:
            return reverse('webapp.postosaurus.views.org.members',
                           args=[self.subdomain])
        else:
            return "/"
    membersurl = property(__membersurl)

    def __unicode__(self):
        return self.name


class MailingList(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization)
    

    class Meta:
        unique_together = (("name", "organization"),)

    def __email(self):
        return "%s@%s.postosaurus.com" % (self.name, self.organization.subdomain)
    email = property(__email)

    def archive_url(self):
        return reverse('webapp.postosaurus.views.list.archive_overview', args=[self.organization.subdomain, self.name])

    def members_url(self):
        return reverse('webapp.postosaurus.views.list.members', args=[self.organization.subdomain, self.name])


    def __unicode__(self):
        return self.name


class Membership(models.Model):

    """
    Indicates a user is a member of an organization.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s:%s" % (self.organization.subdomain, self.user.email)


class Subscription(models.Model):

    """
    Indicates a user is subscribed to a mailing list.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    mailing_list = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return '%s:%s' % (self.mailing_list.name, self.user.email)


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


class Message(models.Model):

    subject = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    mlist = models.ForeignKey(MailingList)

    def __unicode__(self):
        return str(self.id)

            
class File(models.Model):

    message = models.ForeignKey(Message, null=True)
    mlist = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)
    sha = models.CharField(max_length=40, unique = True)
    name = models.CharField(max_length=260)
    ext = models.CharField(max_length=260)
    organization = models.ForeignKey(Organization)
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
                            self.organization.subdomain[0],
                            self.organization.subdomain,
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
                            self.organization.subdomain[0],
                            self.organization.subdomain,
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


        
        



