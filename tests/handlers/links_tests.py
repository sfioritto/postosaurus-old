from config import settings, testing
from lamson import server
from lamson.testing import *
from lamson.mail import MailRequest
from lamson.routing import Router
from webapp.postosaurus.models import *
from nose import with_setup
from email.utils import parseaddr
from app.model import mailinglist
from tests.handlers.admin_tests import test_subscribe_user


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
    clear_queue()
    clear_queue('run/work')


@with_setup(setup_func, teardown_func)
def test_extract_urls_from_text():

    """
    Take the urls from a text email and add
    them to the lists links.
    """
    
    client.begin()
    client.say(list_addr, "Add member to this list. postosaurus.com http://www.google.com")
    mlist = MailingList.objects.filter(email = list_addr)[0]
    assert len(mlist.link_set.all()) == 1
    client.say(list_addr, "Add member to this list. www.postosaurus.com http://www.google.com")
    assert len(mlist.link_set.all()) == 2


@with_setup(setup_func, teardown_func)
def test_text_query_string():

    """
    Given a text email, extract urls with a query string.
    """
    
    client.begin()
    client.say(list_addr, "Add member to this list. www.postosaurus.com/?test=123&herewego=now")
    mlist = MailingList.objects.filter(email = list_addr)[0]
    assert len(mlist.link_set.all()) == 1

    client.say(list_addr, "Add member to this list. www.postosaurus.com/?test=123&herewego=now")
    assert len(mlist.link_set.all()) == 1

    client.say(list_addr, "Add member to this list. www.postosaurus.com/?test=123&herewego=thischanged")
    assert len(mlist.link_set.all()) == 2


@with_setup(setup_func, teardown_func)
def test_chopped_url():
    msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/chopped-url.msg").read())
    Router.deliver(msg)
    mlist = MailingList.objects.filter(email = list_addr)[0]
    links = mlist.link_set.all()
    assert len(links) == 2
    assert 'http://www.artic.edu/aic/collections/artwork/34145' in [link.url for link in links]


@with_setup(setup_func, teardown_func)
def test_long_url_1():
    msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/long-url-1.msg").read())
    Router.deliver(msg)
    mlist = MailingList.objects.filter(email = list_addr)[0]
    links = mlist.link_set.all()
    assert len(links) == 1
    assert 'http://www.google.com/reader/view/#stream/feed%2Fhttp%3A%2F%2Fsethgodin.typepad.com%2Fseths_blog%2Findex.rdf' in [link.url for link in links]


@with_setup(setup_func, teardown_func)
def test_two_urls():
    msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/two-urls.msg").read())
    Router.deliver(msg)
    mlist = MailingList.objects.filter(email = list_addr)[0]
    links = mlist.link_set.all()
    assert len(links) == 2
    assert 'http://www.rolfnelson.com/2009/11/your-work-habits-and-happiness.html' in [link.url for link in links]
    assert 'http://www.rolfnelson.com/2009/11/how-to-follow-through-emerging-science.html' in [link.url for link in links]








