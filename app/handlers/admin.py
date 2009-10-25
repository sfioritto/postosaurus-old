import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay
from lamson import view
from app.model import mailinglist



@route('(list_name)@(host)')
def POSTING(message, list_name=None, host=None):
    if mailinglist.is_subscribed(message['from'], list_name):
        mailinglist.post_message(relay, message, list_name, host, message['from'])
    return POSTING


@route_like(POSTING)
def START(message, list_name=None, host=None):
    print '!!!!!!!!!!!!!!!!!!!!'
    print message.base.keys()
    POSTING(message, list_name=list_name, host=host)

