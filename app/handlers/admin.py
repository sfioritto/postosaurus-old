import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, CONFIRM
from lamson import view, queue
from app.model import mailinglist, links, archive, confirm
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


    list_addr = "%s@%s" % (list_name, host)
    if mailinglist.is_subscribed(message['from'], list_name):

        #send a request for confirmation to anyone cc'd on this list so they can
        #join the group if they want.    
        allrecpts = mailinglist.all_recpts(message)
        for address in [to for to in allrecpts if not to.endswith(host)]:
            CONFIRM.send_if_not_subscriber(relay, mlist, 'confirm', address, 'postosaurus/join-confirmation.msg')

        delivery = mailinglist.craft_response(message, list_name, list_addr) 
        mailinglist.post_message(relay, message, delivery, list_name, host, message['from'])

        q = queue.Queue("run/work")
        q.push(delivery)

    return POSTING


@route('(list_name)-confirm-(id_number)@(host)')
def START(message, list_name=None, id_number=None, host=None):
    
    """
    The start state looks for confirmation emails and move users with valid
    confirmation emails into a posting state. We also create the user's
    postosaurus account (if needed) and subscription here.

    This prevents users from being added to a list if they
    don't want to be.
    """

    mlist = mailinglist.find_list(list_name)
    if mlist:
        if CONFIRM.verify(mlist, 'confirm', message['from'], id_number):

            # Let them know they've been added.
            CONFIRM.notify(relay, mlist, target, message['from'])

            user = mailinglist.find_user(address)
            if not user:
                user = mailinglist.create_user(address)
            mailinglist.add_if_not_subscriber(address, list_name)

            return POSTING

    return START

