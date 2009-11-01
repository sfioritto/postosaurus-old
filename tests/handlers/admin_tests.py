from lamson.testing import *
from lamson import server
from webapp.postosaurus.models import *
from nose import with_setup
from email.utils import parseaddr
from app.model import mailinglist

relay = relay(port=8823)
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


def teardown_func():
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()    


def subscribe_user(address):
    mlist = MailingList.objects.filter(email = list_addr)[0]
    mlist.save()
    sub_name, sub_addr = parseaddr(address)
    print sub_addr
    user = mailinglist.create_user(sub_addr)
    mailinglist.add_if_not_subscriber(address, list_name)


@with_setup(setup_func, teardown_func)
def test_add_new_user():

    """
    If there are multiple addresses in the To field, add them
    tot the list.
    """
    
    client.begin()
    subscribe_user(sender)
    client.say([list_addr, member], "Add member to this list.")
    mlist = MailingList.objects.filter(email = list_addr)[0]
    assert len(mlist.subscription_set.all()) == 2
    

@with_setup(setup_func, teardown_func)
def test_subscribers_no_duplicates():
    
    """
    If an email address in the To field is from someone in
    the list already, the list should not generate a
    duplicate email.
    """

    client.begin()
    test_add_new_user()
    assert queue().count() == 0, "There are %s messages in the queue should be 0." % queue().count()

@with_setup(setup_func, teardown_func)
def test_existing_user_posts_message():

    """
    Posts a message and checks to see that the one member
    was sent a message.
    """

    client.begin()
    subscribe_user(sender)
    subscribe_user(member)
    test_forwards_to_posting()
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


@with_setup(setup_func, teardown_func)
def test_forwards_to_posting():

    """
    Makes sure that the first message sent moves a user into the POSTING state.
    """

    subscribe_user(sender)
    client.begin()
    client.say(list_addr, "Test that forward works.")
    name, addr = parseaddr(sender)
    assert_in_state('app.handlers.admin', list_addr, addr, 'POSTING')







