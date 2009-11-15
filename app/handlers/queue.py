import re
from app.model import links, archive
from lamson.routing import route, stateless
from lamson import queue
from django.db import transaction

@route("(list_name)@(host)")
@stateless
@transaction.commit_manually
def START(message, list_name=None, host=None):

    try:
        dbmessage = archive.store_message(list_name, message)

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



