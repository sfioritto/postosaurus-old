from lamson.testing import *
from lamson.mail import MailRequest
from lamson.routing import Router
from config import settings, testing
from webapp import settings as websettings
from webapp.postosaurus.models import *
from nose import with_setup
from app.model import mailinglist, files
from tests.handlers.admin_tests import test_subscribe_user
import os
import shutil


sender = "Beth Lukes <beth.lukes@gmail.com>"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
client = RouterConversation(sender, 'Admin Tests')

deneen_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/deneen-attachment.msg").read())
text_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/text-attachment.msg").read())
two_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/two-attachments.msg").read())


def setup_func():

    Subscription.objects.all().delete()
    User.objects.all().delete()

    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()

    if os.path.isdir(websettings.FILES_DIR):
        shutil.rmtree(websettings.FILES_DIR)
    os.mkdir(websettings.FILES_DIR)


def teardown_func():
    # clear the database
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_one_attachment():
    test_subscribe_user(sender=sender, client=client)
    Router.deliver(deneen_msg)
    mlist = mailinglist.find_list(list_name)
    assert len(mlist.message_set.all()) == 1
    msg = mlist.message_set.all()[0]
    
    assert len(msg.file_set.all()) == 1
    attached = msg.file_set.all()[0]
    path = attached.pathprefix
    assert os.listdir(path)[0] == attached.hash_name()


@with_setup(setup_func, teardown_func)
def test_two_attachments():
    test_subscribe_user(sender=sender, client=client)
    Router.deliver(two_msg)
    mlist = mailinglist.find_list(list_name)
    assert len(mlist.message_set.all()) == 1

    msg = mlist.message_set.all()[0]
    assert len(msg.file_set.all()) == 2
    attached = msg.file_set.all()[0]
    path = attached.pathprefix
    assert os.listdir(path)[0] == attached.hash_name()

    attached = msg.file_set.all()[1]
    path = attached.pathprefix
    assert os.listdir(path)[1] == attached.hash_name()




