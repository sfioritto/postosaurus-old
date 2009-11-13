from nose import with_setup
from webapp.postosaurus.models import *
from app.model import archive, mailinglist
from app.model.archive import archive as arch
from lamson.mail import MailResponse
from datetime import datetime
import simplejson as json

host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
url = "http://www.postosaurus.com"

message = MailResponse(To=list_addr, From='sender@sender.com', Subject="no subject", Body="body")


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
def test_add_message():

    """
    Adds a message to the archive.
    """

    dbmessage = archive.store_message(list_name, message)

    assert dbmessage.subject == message['Subject']
    assert json.dumps(archive.get_message(str(dbmessage.id)), sort_keys=True) == archive.to_json(message.base)


@with_setup(setup_func, teardown_func)
def test_get_messages():

    test_add_message()
    mlist = mailinglist.find_list(list_name)
    dbmessage = Message.objects.filter(mlist=mlist).all()[0]
    key = str(dbmessage.id)
    messages = archive.get_messages([key])
    assert len(messages) == 1
    rmessage = archive.get_message(key)
    assert json.dumps(rmessage, sort_keys=True) == archive.to_json(message.base)
    
    
    

    


    


