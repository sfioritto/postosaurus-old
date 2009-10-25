from lamson.testing import *
from lamson import server
from webapp.postosaurus.models import *
from nose import with_setup


relay = relay(port=8823)
sender = "sender@sender.com"
member = "member@member.com"
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
    user = User(email = address)
    user.save()
    if not Subscription.objects.filter(user=user, mailing_list = mlist):
        sub = Subscription(user=user, mailing_list = mlist)
        sub.save()


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
    assert_in_state('app.handlers.admin', list_addr, sender, 'POSTING')





