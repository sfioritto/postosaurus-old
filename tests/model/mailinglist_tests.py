from webapp.postosaurus.models import *
from nose import with_setup
from app.model import mailinglist


member = "member@member.com"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()


def teardown_func():
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()    


@with_setup(setup_func, teardown_func)
def test_create_user():

    """
    Create a user.
    """

    user = mailinglist.create_user(member)
    assert len(User.objects.all()) == 1
    user = mailinglist.create_user(member)
    assert len(User.objects.all()) == 1


@with_setup(setup_func, teardown_func)
def test_add_if_not_subscribed():
    """
    Test add_if_not_subscribed.
    """
    test_create_user()
    mailinglist.add_if_not_subscriber(member, list_name)
    subs = Subscription.objects.all()
    assert len(subs) == 1
    mailinglist.add_if_not_subscriber(member, list_name)
    assert len(subs) == 1


