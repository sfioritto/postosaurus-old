from django.db import models
from datetime import datetime
from email.utils import formataddr

class MailingList(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name


class Subscription(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    subscriber_address = models.EmailField()
    subscriber_name = models.CharField(max_length=200)
    mailing_list = models.ForeignKey(MailingList)

    def __unicode__(self):
        return '"%s" <%s>' % (self.subscriber_name, self.subscriber_address)

    def subscriber_full_address(self):
        return formataddr((self.subscriber_name, self.subscriber_address))
