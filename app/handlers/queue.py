import re
from app.model import links, archive
from lamson.routing import route, stateless


@route("(list_name)@(host)")
@stateless
def START(message, list_name=None, host=None):

    dbmessage = archive.store_message(list_name, message)

    body = message.body()

    if body:
        urls = links.extract_urls_from_text(body)
        for url in urls:
            links.add_link(list_name, url, dbmessage)
