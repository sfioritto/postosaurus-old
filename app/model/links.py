import re
from webapp.postosaurus.models import *
from email.utils import parseaddr
from lamson.mail import MailResponse

def enqueue(*args, **kwargs):
    pass

# def post_message(relay, message, list_name, host, fromaddress):
#     name, addr = parseaddr(fromaddress)
#     mlist = find_list(list_name)
#     sender = find_user(addr)
#     assert mlist, "User is somehow able to post to list %s" % list_name
#     assert sender, "Sender %s must exist in order to post a message" % addr

#     for sub in mlist.subscription_set.all():
#         if should_generate_response(sub.user, sender, message):
#             list_addr = "%s@%s" % (list_name, host)
#             delivery = craft_response(message, list_name, list_addr) 
#             relay.deliver(delivery, To=sub.user.email, From=list_addr)

