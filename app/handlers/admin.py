from lamson.routing import route, route_like, stateless, state_key_generator
from config.settings import relay, CONFIRM
from lamson import view, queue
from app.model import mailinglist
from types import ListType
from email.utils import parseaddr

@state_key_generator
def module_and_listname(modulename, message):

    name, address = parseaddr(message['to'])
    if '-' in address:
        listname = address.split('-')[0]
    else:
        listname = address.split('@')[0]

    return modulename + ':' + listname


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
            name, address = parseaddr(message['from'])
            CONFIRM.notify(relay, mlist, 'confirm', address)
            user = mailinglist.find_user(address)
            if not user:
                user = mailinglist.create_user(address)
            mailinglist.add_if_not_subscriber(address, list_name)
            return POSTING
    return START


@route('(list_name)@(host)')
@route_like(START)
def POSTING(message, list_name=None, id_number=None, host=None):

    """
    Takes a message and posts it to the rest of the group. If there
    are multiple email addresses in the To or CC field, those emails
    will be added to the list.

    We also ensure that they don't receive a duplicate of the
    email they were just sent.
    """

    #an existing user is adding themselves to another group.
    if id_number:
        START(message, list_name=list_name, id_number=id_number, host=None)

    else:

        list_addr = "%s@%s" % (list_name, host)
        if mailinglist.is_subscribed(message['from'], list_name) and mailinglist.is_active(list_name):
            mlist = mailinglist.find_list(list_name)

        #send a request for confirmation to anyone cc'd on this list so they can
        #join the group if they want.    
            allrecpts = mailinglist.all_recpts(message)
            for address in [to for to in allrecpts if not to.endswith(host)]:
                CONFIRM.send_if_not_subscriber(relay, mlist, 'confirm', address, 'postosaurus/join-confirmation.msg', host)

            delivery = mailinglist.craft_response(message, list_name, list_addr)
            mailinglist.post_message(relay, message, delivery, list_name, host, message['from'])

            q = queue.Queue("run/work")
            q.push(message)

    return POSTING
