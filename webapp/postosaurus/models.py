from django.db import models
from datetime import datetime
from email.utils import formataddr


class User(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, auto_now=True)
    email = models.CharField(max_length=512, primary_key=True)

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

            
class Link(models.Model):
    mlist = models.ForeignKey(MailingList)
    url = models.CharField(max_length=2083)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.url
    def cleaned(self):
        return self.url
    

class Message(models.Model):
    mlist = models.ForeignKey(MailingList)
    user = models.ForeignKey(User)
    subject = models.CharField(max_length=2083)
    text = models.CharField(max_length=40000)
    created_on = models.DateTimeField(auto_now_add=True)
