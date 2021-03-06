from lamson.testing import *
from lamson import server, routing
from webapp.postosaurus.models import *
from nose import with_setup
from email.utils import parseaddr
from app.model import mailinglist
from config.settings import CONFIRM

relay = relay(port=8825)
sender = "send <sender@sender.com>"
member = "member <member@member.com>"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
client = RouterConversation(sender, 'Admin Tests')
mclient = RouterConversation(member, 'Admin Tests')
user = None


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()


def teardown_func():
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()    
    JoinConfirmation.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_subscribe_user(sender=sender, client=client, mlist=None):

    if not mlist:
        mlist = MailingList.objects.filter(email = list_addr)[0]
    subs = len(mlist.subscription_set.all())
    msg = CONFIRM.send_if_not_subscriber(relay, mlist, 'confirm', sender, 'postosaurus/join-confirmation.msg', host)
    client.say(msg['from'], "subscribe me")
    newsubs = len(mlist.subscription_set.all())
    assert newsubs == subs + 1, "Should be %s subscriptions but there are %s" % (str(subs + 1), str(newsubs))
    assert_in_state('app.handlers.admin', msg['from'], msg['to'], 'POSTING')


@with_setup(setup_func, teardown_func)
def test_existing_user_new_list():

    test_subscribe_user()
    mlist = MailingList(name = 'newlist', email = 'newlist@postosaurus.com')
    mlist.save()
    subs = len(mlist.subscription_set.all())
    assert subs == 0
    
    msg = CONFIRM.send_if_not_subscriber(relay, mlist, 'confirm', sender, 'postosaurus/join-confirmation.msg', host)
    client.say(msg['from'], "subscribe me")
    newsubs = len(mlist.subscription_set.all())
    assert newsubs == subs + 1, "Should be %s subscriptions but there are %s" % (str(subs + 1), str(newsubs))
    assert_in_state('app.handlers.admin', msg['from'], msg['to'], 'POSTING')


@with_setup(setup_func, teardown_func)
def test_add_new_user():

    """
    If there are multiple addresses in the To field, add them
    to the list.
    """
    
    client.begin()
    test_subscribe_user()
    client.say([list_addr, member], "Add member to this list.")
    mlist = MailingList.objects.filter(email = list_addr)[0]
    assert len(mlist.subscription_set.all()) == 1
    assert len(JoinConfirmation.objects.all()) == 1

    test_subscribe_user(member, mclient)
    assert len(mlist.subscription_set.all()) == 2
    

@with_setup(setup_func, teardown_func)
def test_subscribers_no_duplicates():
    
    """
    If an email address in the To field is from someone in
    the list already, the list should not generate a
    duplicate email.
    """

    test_add_new_user()
    client.begin()
    assert queue().count() == 0, "There are %s messages in the queue should be 0." % queue().count()

@with_setup(setup_func, teardown_func)
def test_existing_user_posts_message():

    """
    Posts a message and checks to see that the one member
    was sent a message.
    """

    client.begin()
    test_subscribe_user()
    test_subscribe_user(member, mclient)
    clear_queue()
    msg = client.say(list_addr, "My first message.")
    # only one message should be sent to member.
    assert queue().count() == 1


@with_setup(setup_func, teardown_func)
def test_non_user_posts_message():
    
    """
    Only subscribers to a list can post to the list.
    """

    assert len(User.objects.all()) == 0
    client.begin()
    msg = client.say(list_addr, "My first message.")
    assert not delivered(list_addr)
