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
subdomain = "admin"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s.%s" % (list_name, subdomain, host)
client = RouterConversation(sender, 'Admin Tests')
user = None


def setup_func():
    user = User(email="bob@bob.com")
    user.save()
    org = Organization(name=subdomain, subdomain=subdomain, owner=user, active=True)
    org.save()
    mlist = MailingList(name=list_name, organization=org)
    mlist.save()
    sender_name, sender_addr = parseaddr(sender)
    user = mailinglist.create_user(sender_addr)
    mailinglist.add_if_not_subscriber(sender, list_name, org)
    user.save()


def teardown_func():
    Organization.objects.all().delete()
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()
    Message.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_archive_message():

    """
    Make sure messages sent are archived under the correct group.
    """
    
    client.begin()
    client.say(list_addr, "Stuff.")
    mlist = mailinglist.find_list(list_name, subdomain)
    assert len(mlist.message_set.all()) == 1
    client.say(list_addr, "More stuff")
    assert len(mlist.message_set.all()) == 2


@with_setup(setup_func, teardown_func)
def test_complicated_archive_message():
    #NOTE: the address the message is delivered to is hardcoded in the message itself.
    msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/archive.msg").read())
    Router.deliver(msg)
    mlist = mailinglist.find_list(list_name, subdomain)
    messageid = mlist.message_set.all()[0].id
    jsmsg = json.loads(arch[str(messageid)])
    assert jsmsg['body'] == None
    assert len(jsmsg['parts']) == 2
    assert 'opted' in jsmsg['parts'][0]['body']
    assert len(mlist.message_set.all()) == 1


def test_to_json():
    msg = MailRequest('fakeperr', None, None, open("tests/data/bounce.msg").read())

    resp = mailinglist.craft_response(msg, 'test.list', 'test.list@librelist.com')

    resp.attach(filename="tests/data/bounce.msg", content_type="image/png", disposition="attachment")
    resp.to_message() 

    js = archive.to_json(resp.base)
    assert js

    rtjs = json.loads(js)
    assert rtjs
    assert rtjs['parts'][-1]['encoding']['format'] == 'base64'
