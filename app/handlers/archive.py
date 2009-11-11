import re
from app.model import links
from lamson.routing import route, stateless


@route("(list_name)@(host)")
@stateless
def START(message, list_name=None, host=None):
    import logging
    logging.debug("archive some shit")
