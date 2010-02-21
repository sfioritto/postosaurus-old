import re
from app.model import archive, files, mailinglist
from lamson.routing import route, stateless
from lamson import queue
from django.db import transaction

@route("(list_name)@(subdomain)\.(host)")
@stateless
@transaction.commit_manually
def START(message, list_name=None, subdomain=None, host=None):
    
    """
    This is the central logic for doing most of the stuff
    that makes Postosaurus worth paying money for.
    """

    try:

        org = mailinglist.find_org(subdomain)
        #db message is the message record created in the database. The
        #id generated is used as a key to extract the actual message
        #from tokyo tyrant. We do this so that it's easy to maintain
        # relational data, like what files are related to a message? A
        # key value store is not good at storing this kind of data.
        dbmessage = archive.store_message(list_name, message, org)

        # store attached files for retrieval
        for name in files.file_names(message):
            files.store_file_from_message(list_name, org, message, name, dbmessage)

        transaction.commit()

    except:
        #queue up any messages that failed so we can diagnose
        #and try later.
        transaction.rollback()
        q = queue.Queue("run/error")
        q.push(message)



