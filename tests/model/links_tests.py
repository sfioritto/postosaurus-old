from webapp.postosaurus.models import *
from nose import with_setup
from app.model import links, mailinglist


host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
url = "http://www.postosaurus.com"


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()


def teardown_func():
    MailingList.objects.all().delete()
    Link.objects.all().delete()

    
@with_setup(setup_func, teardown_func)
def test_add_link():

    """
    Add a link.
    """

    links.add_link(list_name, url)
    assert len(Link.objects.all()) == 1

@with_setup(setup_func, teardown_func)
def test_add_existing_link():
    
    """
    Try to add a link that has already been added.
    """

    test_add_link()
    assert len(Link.objects.all()) == 1
    links.add_link(list_name, url)
    assert len(Link.objects.all()) == 1


@with_setup(setup_func, teardown_func)
def test_link_not_added():
    """
    Check query for determining whether a link has already been added
    or not.
    """

    mlist = mailinglist.find_list(list_name)
    assert links.not_added(mlist, url)
    test_add_link()
    assert links.not_added(mlist, url) == False
    


