from lamson.testing import *
from lamson.mail import MailRequest
from lamson.routing import Router
from lamson import server
from webapp.postosaurus.models import *
from nose import with_setup
from email.utils import parseaddr
from app.model import mailinglist, archive
from app.model.archive import archive as arch
import simplejson as json


sender = "send <sender@sender.com>"
member = "member <member@member.com>"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
client = RouterConversation(sender, 'Admin Tests')
user = None


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()
    sender_name, sender_addr = parseaddr(sender)
    user = mailinglist.create_user(sender_addr)
    mailinglist.add_if_not_subscriber(sender, list_name)
    user.save()


def teardown_func():
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()
    Link.objects.all().delete()
    Message.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_archive_message():

    """
    Make sure messages sent are archived under the correct group.
    """
    
    client.begin()
    client.say(list_addr, "Add member to this list. postosaurus.com http://www.google.com")
    mlist = MailingList.objects.filter(email = list_addr)[0]
    assert len(mlist.message_set.all()) == 1
    client.say(list_addr, "Add member to this list. www.postosaurus.com http://www.google.com")
    assert len(mlist.message_set.all()) == 2


@with_setup(setup_func, teardown_func)
def test_complicated_archive_message():
    msg = MailRequest('fakeperr', sender, list_addr, open("tests/archive.msg").read())
    Router.deliver(msg)
    mlist = MailingList.objects.filter(email = list_addr)[0]
    messageid = mlist.message_set.all()[0].id
    jsmsg = json.loads(arch[str(messageid)])
    assert jsmsg['body'] == None
    assert len(jsmsg['parts']) == 2
    assert 'opted' in jsmsg['parts'][0]['body']
    assert len(mlist.message_set.all()) == 1
    

def test_to_json():
    msg = MailRequest('fakeperr', None, None, open("tests/bounce.msg").read())

    resp = mailinglist.craft_response(msg, 'test.list', 'test.list@librelist.com')

    resp.attach(filename="tests/bounce.msg", content_type="image/png", disposition="attachment")
    resp.to_message() 

    js = archive.to_json(resp.base)
    assert js

    rtjs = json.loads(js)
    assert rtjs
    assert rtjs['parts'][-1]['encoding']['format'] == 'base64'
