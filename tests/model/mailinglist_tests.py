from webapp.postosaurus.models import *
from nose import with_setup
from app.model import mailinglist


subdomain = "mailinglist"
member = "member@member.com"
host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s.%s" % (list_name, subdomain, host)


def setup_func():
    user = User(email="bob@bob.com")
    user.save()
    org = Organization(name=subdomain, subdomain=subdomain, owner=user, active=True)
    org.save()
    mlist = MailingList(name = list_name,
                        organization = org)
    mlist.save()


def teardown_func():
    Organization.objects.all().delete()
    MailingList.objects.all().delete()
    Subscription.objects.all().delete()
    User.objects.all().delete()    

teardown_func()

@with_setup(setup_func, teardown_func)
def test_create_user():

    """
    Create a user.
    """

    user = mailinglist.create_user(member)
    assert len(User.objects.all()) == 2
    user = mailinglist.create_user(member)
    assert len(User.objects.all()) == 2


@with_setup(setup_func, teardown_func)
def test_add_if_not_subscribed():
    """
    Test add_if_not_subscribed.
    """
    org = mailinglist.find_org(subdomain)
    test_create_user()
    mailinglist.add_if_not_subscriber(member, list_name, org)
    subs = Subscription.objects.all()
    assert len(subs) == 1
    mailinglist.add_if_not_subscriber(member, list_name, org)
    assert len(subs) == 1


