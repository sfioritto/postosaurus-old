import re
from app.model import archive
from lamson.routing import route, stateless


@route("(list_name)@(host)")
@stateless
def START(message, list_name=None, host=None):
    list_addr = "%s@%s" % (list_name, host)
    archive.store_message(list_addr, message)
