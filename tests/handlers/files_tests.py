from lamson.testing import *
from lamson.mail import MailRequest
from lamson.routing import Router
from webapp import settings as websettings
from config import settings, testing
from webapp.postosaurus.models import *
from nose import with_setup
from app.model import mailinglist, files
from tests.handlers.admin_tests import test_subscribe_user
from email.utils import parseaddr
import os
import shutil
import config

sender = "send <sender@sender.com>"
subdomain = "files"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s.%s" % (list_name, subdomain, host)
sender_client = RouterConversation(sender, 'Files Tests')

deneen_msg = MailRequest('fakepeer', 'beth.lukes@gmail.com', list_addr, open("tests/data/deneen-attachment.msg").read())
text_msg = MailRequest('fakepeer', 'sean.fioritto@gmail.com', list_addr, open("tests/data/text-attachment.msg").read())
two_msg = MailRequest('fakepeer', 'beth.lukes@gmail.com', list_addr, open("tests/data/two-attachments.msg").read())
gzip_msg = MailRequest('fakepeer', 'sean@allicator.com', list_addr, open("tests/data/gzip-attachment.msg").read())


def setup_func():
    
    Organization.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()

    user = User(email="bob@bob.com")
    user.save()
    org = Organization(name=subdomain, subdomain=subdomain, owner=user, active=True)
    org.save()
    mlist = MailingList(name=list_name, organization=org)
    mlist.save()

    if os.path.isdir(websettings.FILES_DIR):
        shutil.rmtree(websettings.FILES_DIR)
    os.mkdir(websettings.FILES_DIR)


def teardown_func():

    # clear the database

    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()
    UserState.objects.all().delete()
    Organization.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_one_attachment():

    #subscribe the original sender
    name, address = parseaddr(deneen_msg['from'])
    client = RouterConversation(address, 'Files Tests')
    mlist = mailinglist.find_list(list_name, subdomain)
    test_subscribe_user(sender=address, client=client, mlist=mlist)

    # add someone else to the list
    test_subscribe_user(sender=sender, client=sender_client, mlist=mlist)

    # update the message to send to the list we just created.
    deneen_msg['to'] = list_addr
    
    Router.deliver(deneen_msg)
    mlist = mailinglist.find_list(list_name, subdomain)
    assert len(mlist.message_set.all()) == 1
    msg = mlist.message_set.all()[0]
    
    assert len(msg.file_set.all()) == 1
    attached = msg.file_set.all()[0]
    path = os.path.join(attached.pathprefix, attached.sha)
    assert attached.name in os.listdir(path)
    assert_in_state('app.handlers.admin', deneen_msg['to'], address, 'POSTING')


@with_setup(setup_func, teardown_func)
def test_two_attachments():
    name, address = parseaddr(deneen_msg['from'])
    client = RouterConversation(address, 'Files Tests')
    mlist = mailinglist.find_list(list_name, subdomain)
    test_subscribe_user(sender=address, client=client, mlist=mlist)

    Router.deliver(two_msg)
    mlist = mailinglist.find_list(list_name, subdomain)
    assert len(mlist.message_set.all()) == 1

    msg = mlist.message_set.all()[0]
    assert len(msg.file_set.all()) == 2
    attached = msg.file_set.all()[0]
    path = os.path.join(attached.pathprefix, attached.sha)
    assert os.listdir(path)[0] == attached.name

    attached = msg.file_set.all()[1]
    path = os.path.join(attached.pathprefix, attached.sha)
    assert os.listdir(path)[0] == attached.name


@with_setup(setup_func, teardown_func)
def test_gzip_attachment():

    clear_queue()
    
    # set up list and message
    name, address = parseaddr(gzip_msg['from'])
    client = RouterConversation(address, 'Files Tests')
    client.begin()
    mlist = mailinglist.find_list(list_name, subdomain)
    test_subscribe_user(sender=address, client=client, mlist=mlist)
    
    test_subscribe_user(sender=parseaddr(sender)[1], client=sender_client, mlist=mlist)
    gzip_msg['to'] = list_addr

    # deliver the message.
    clear_queue()
    Router.deliver(gzip_msg)

    assert len(mlist.message_set.all()) == 1
    msg = mlist.message_set.all()[0]
    
    assert len(msg.file_set.all()) == 1
    attached = msg.file_set.all()[0]
    path = os.path.join(attached.pathprefix, attached.sha)
    assert attached.name in os.listdir(path)
    assert queue().count() == 1, "Should be 1 message in queue, but there are %s" % queue().count()




