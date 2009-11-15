import lamson.queue as queue
import pytyrant
import simplejson as json
import base64
import hashlib
import datetime
from types import ListType
from webapp.postosaurus.models import Message
from app.model import mailinglist

archive = pytyrant.PyTyrant.open('127.0.0.1', 1978)


def json_encoding(base):
    ctype, ctp = base.content_encoding['Content-Type']
    cdisp, cdp = base.content_encoding['Content-Disposition']
    ctype = ctype or "text/plain"
    filename = ctp.get('name',None) or cdp.get('filename', None)

    if ctype.startswith('text') or ctype.startswith('message'):
        encoding = None
    else:
        encoding = "base64"

    return {'filename': filename, 'type': ctype, 'disposition': cdisp,
            'format': encoding}


def json_build(base):
    data = {'headers': base.headers,
                'body': base.body,
                'encoding': json_encoding(base),
                'parts': [json_build(p) for p in base.parts],
            }

    if data['encoding']['format'] and base.body:
        data['body'] = base64.b64encode(base.body)

    return data


def to_json(base):
    return json.dumps(json_build(base), sort_keys=True)


def messages_by_day(listname, year, month, day):

    """
    Returns all messages for the given list and day.
    """

    mlist = mailinglist.find_list(listname)
    start = datetime.datetime(year, month, day)
    end = start + datetime.timedelta(hours=23, minutes=59, seconds=59)
    dbmessages = Message.objects\
        .filter(created_on__range=(start, end))\
        .filter(mlist = mlist)\
        .all()
    ids = [str(message.id) for message in dbmessages]
    messages = []
    for msg in archive.multi_get(ids):
        #The archiver sometimes screws up and misses an
        #email. multi_get returns null in that case. Do
        #this check so the json loader doesn't blow up.
        if msg:
            messages.append(json.loads(msg))
            
    return messages
    

def get_message(messagekey):

    """
    Returns a json list for the given key.
    """

    return json.loads(archive[messagekey])


def get_messages(keys):
    
    """
    Returns json messages for the list of
    keys provided.
    """

    assert type(keys) == ListType
    return [json.loads(message) for message in archive.multi_get(keys)]


def store_message(list_name, message):

    """
    Creates entries in key value store so a message can be
    retrieved and days that have messages for a list and messages
    for each of those days. 

    Messages should never be stored directly in the archive or they
    will never be able to be retrieved. Messages should only
    be archived using this function.
    """

    mlist = mailinglist.find_list(list_name)
    dbmessage = Message(mlist=mlist, subject=message['Subject'])
    dbmessage.save()
    mjson = to_json(message.base)
    archive[str(dbmessage.id)] = mjson
    return dbmessage
    
