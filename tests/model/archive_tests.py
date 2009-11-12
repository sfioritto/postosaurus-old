from nose import with_setup
from webapp.postosaurus.models import *
from app.model import archive
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


def test_add_message():

    """
    Adds a message to the archive.
    """

    year, month, day = datetime.utcnow().timetuple()[:3]
    messagekey = archive.message_key(message)
    
    archive.store_message(list_addr, message, year=year, month=month, day=day)
    assert json.dumps(archive.get_message(messagekey), sort_keys=True) == archive.to_json(message.base)
    assert len(archive.messages_by_day(list_addr, year, month, day)) == 1
    assert len(archive.list_active_days(list_addr)) == 1


def test_add_message_to_day():

    """
    Adds a message to a day.
    """

    year, month, day = datetime.utcnow().timetuple()[:3]
    key = archive.message_key(message)
    archive.add_message_to_day(key, list_addr, year, month, day)
    assert len(archive.messages_by_day(list_addr, year, month, day)) == 1



def test_get_messages():

    key = archive.message_key(message)
    messages = archive.get_messages([key])
    assert len(messages) == 1
    rmessage = archive.get_message(key)
    assert json.dumps(rmessage, sort_keys=True) == archive.to_json(message.base)
    
    
    

    


    


