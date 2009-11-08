import re
import logging
from app.model import links
from lamson.routing import route, stateless


@route("(list_name)@(host)")
@stateless
def START(message, list_name=None, host=None):
    body = message.body()
    if body:
        list_addr = "%s@%s" % (list_name, host)
        urls = links.extract_urls(body)
        for url in urls:
            links.add_link(list_addr, url)
