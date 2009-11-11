from nose import with_setup
from webapp.postosaurus.models import *
from app.model import archive
from app.model.archive import archive as arch

host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
url = "http://www.postosaurus.com"


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()


def teardown_func():
    # clear the database
    MailingList.objects.all().delete()

    # clear the mail archive
    for key in arch.keys():
        del arch[key]


@with_setup(setup_func, teardown_func)
def test_archive():

    """
    Archive a message
    """

    arch['test'] = 'me'
    arch.concat('test', 'out')
    assert arch['test'] == 'meout'


@with_setup(setup_func, teardown_func)
def test_message_hash():

    """
    Create a unique hash for a message.
    """

    pass


    


