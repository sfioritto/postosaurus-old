import re
from webapp.postosaurus.models import *
from email.utils import parseaddr
from lamson.mail import MailResponse
from types import ListType



def is_subscribed(address, list_name):
    name, addr = parseaddr(address)
    if find_subscription(addr, list_name):
        return True
    else:
        return False;


def valid_name(name):

    """
    Determines whether the list name is valid
    or not.
    """

    return len(name) <= 100 and re.match("^[a-zA-Z0-9]+\.*[a-zA-Z0-9]+$", name)


def create_list(list_name, owner = None):
    list_name = list_name.lower()
    mlist = find_list(list_name)
    assert valid_name(list_name)
    
    if not mlist:
        mlist = MailingList(name=list_name, email=list_name + '@postosaurus.com', owner=owner)
        mlist.save()

    return mlist


def create_user(address):
    name, addr = parseaddr(address)
    user = find_user(addr)
    if not user:
        user = User(email = addr)
        user.save()
    return user

def find_user(address):
    users = User.objects.filter(email = address)
    if users:
        return users[0]
    else:
        return None

def find_list(list_name):
    mlists = MailingList.objects.filter(name = list_name)
    if mlists:
        return mlists[0]
    else:
        return None

def add_if_not_subscriber(address, list_name):
    mlist = create_list(list_name)
    sub_name, sub_addr = parseaddr(address)
    sub = find_subscription(sub_addr, list_name)
    user = find_user(sub_addr)

    if not sub:
        sub = Subscription(mailing_list = mlist,
                           user = user)
        sub.save()
        return sub
    else:
        return sub

def find_subscription(address, list_name):

    sub_name, sub_addr = parseaddr(address)
    mlist = find_list(list_name)
    user = find_user(address)
    if user:
        assert mlist, "Mailing list %s must exist to find a subscription." % list_name
        assert user, "Address must map to user %s to find a subscription." % address
    
        subs = Subscription.objects.filter(mailing_list = mlist, 
                                           user = user)

        if subs:
            return subs[0]
    else:
        return None


def is_active(list_name):
    mlist = find_list(list_name)
    assert mlist, "The list %s needs to actually exist." % list_name
    return mlist.active


def post_message(relay, message, delivery, list_name, host, fromaddress):
    
    """
    Takes a message and delivers it to everyone in the group
    that should receive it.
    """

    name, addr = parseaddr(fromaddress)
    mlist = find_list(list_name)
    sender = find_user(addr)
    assert mlist, "User is somehow able to post to list %s" % list_name
    assert sender, "Sender %s must exist in order to post a message" % addr

    list_addr = "%s@%s" % (list_name, host)
    for sub in mlist.subscription_set.all():
        if should_generate_response(sub.user, sender, message):
            relay.deliver(delivery, To=sub.user.email, From=list_addr)


def all_recpts(message):

    """
    Returns a cleaned up list of all emails in the
    to and Cc headers of the message.
    """

    allrecpts = []

    if type(message.To) == ListType:
        allrecpts = message.To

    if message.base.headers.has_key('To'):
        allrecpts = allrecpts + message.base.headers['To'].split(",")

    if message.base.headers.has_key('Cc'):
        allrecpts = allrecpts + message.base.headers['Cc'].split(",")

    allrecpts = [parseaddr(address)[1] for address in allrecpts]
    
    return allrecpts



def should_generate_response(user, sender, message):
    
    """
    Returns true or false to indicate whether the passed in
    user should receive a response generated by the list.

    In general the sender should not get an email back
    from postosaurus, also if the user is in the To
    field of the message, they would get a duplicate
    message, so we don't generate a response.
    """
    allrecpts = all_recpts(message)
    if user.email in allrecpts:
        return False

    elif user == sender:
        return False

    else:
        return True
    


def craft_response(message, list_name, list_addr):
    response = MailResponse(To=list_addr, 
                            From=message['from'],
                            Subject=message['subject'])

    msg_id = message['message-id']

    response.update({
        "Sender": list_addr, 
        "Reply-To": list_addr,
        "List-Id": list_addr,
        "List-Unsubscribe": "<mailto:%s-unsubscribe@postosaurus.com>" % list_name,
        "List-Archive": "<http://postosaurus.com/archives/%s/>" % list_name,
        "List-Post": "<mailto:%s>" % list_addr,
        "List-Help": "<http://postosaurus.com/help.html>",
        "List-Subscribe": "<mailto:%s-subscribe@postosaurus.com>" % list_name,
        "Return-Path": list_addr, 
        "Precedence": 'list',
    })

    if 'date' in message:
        response['Date'] = message['date']

    if 'references' in message:
        response['References'] = message['References']
    elif msg_id:
        response['References'] = msg_id

    if msg_id:
        response['message-id'] = msg_id

        if 'in-reply-to' not in message:
            response["In-Reply-To"] = message['Message-Id']

    if message.all_parts():
        for part in message.all_parts():
            if part:
                response.attach_part(part)

        response.base.content_encoding = message.base.content_encoding.copy()
    else:
        response.Body = message.body()

    return response






