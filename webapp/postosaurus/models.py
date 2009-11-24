from django.db import models
from datetime import datetime
from email.utils import formataddr
from django.contrib.auth.models import User as DjangoUser


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

    def __unicode__(self):
        return self.name


class Subscription(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    mailing_list = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return '%s' % (self.user.email)


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
    








