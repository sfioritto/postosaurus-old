import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay
from lamson import view, queue
from app.model import mailinglist, links, archive
from types import ListType
from email.utils import parseaddr


@route('(list_name)@(host)')
def POSTING(message, list_name=None, host=None):

    """
    Takes a message and posts it to the rest of the group. If there
    are multiple email addresses in the To or CC field, those emails
    will be added to the list.

    We also ensure that they don't receive a duplicate of the
    email they were just sent.
    """

    allrecpts = mailinglist.all_recpts(message)
    
    for address in [to for to in allrecpts if not to.endswith(host)]:
        user = mailinglist.find_user(address)
        if not user:
            mailinglist.create_user(address)
        mailinglist.add_if_not_subscriber(address, list_name)

    list_addr = "%s@%s" % (list_name, host)
    if mailinglist.is_subscribed(message['from'], list_name):
        delivery = mailinglist.craft_response(message, list_name, list_addr) 
        mailinglist.post_message(relay, message, delivery, list_name, host, message['from'])
        #if we end up with a queue model file, put this in there.
        q = queue.Queue("run/work")
        q.push(delivery)

    return POSTING


@route_like(POSTING)
def CONFIRMING_SUBSCRIBE(message, list_name=None, host=None):
    pass


@route_like(POSTING)
def START(message, list_name=None, host=None):
    return POSTING(message, list_name=list_name, host=host)

