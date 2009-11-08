from lamson.routing import route, stateless
import logging

@route("(list_name)@(host)")
@stateless
def START(message, list_name=None, host=None):
    logging.debug("Got message from %s", message['from'])
