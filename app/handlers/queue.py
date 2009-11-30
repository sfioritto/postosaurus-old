import re
from app.model import links, archive, files
from lamson.routing import route, stateless
from lamson import queue
from django.db import transaction

@route("(list_name)@(host)")
@stateless
@transaction.commit_manually
def START(message, list_name=None, host=None):
    
    """
    This is the central logic for doing most of the stuff
    that makes Postosaurus worth paying money for. Right
    now we pull a message off of the work queue, archive it
    and extract any links.
    """

    try:
        #db message is the message record created in the database. The
        #id generated is used as a key to extract the actual message
        #from tokyo tyrant. We do this so that it's easy to maintain
        # relational data, like what links are related to a message? A
        # key value store is not good at storing this kind of data.
        dbmessage = archive.store_message(list_name, message)
        
        for name in files.file_names(message):
            files.store_file(list_name, message, name, dbmessage)
        body = message.body()
        if body:
            urls = links.extract_urls_from_text(body)
            for url in urls:
                links.add_link(list_name, url, dbmessage)
        transaction.commit()

    except:
        #queue up any messages that failed so we can diagnose
        #and try later.
        transaction.rollback()
        q = queue.Queue("run/error")
        q.push(message)



