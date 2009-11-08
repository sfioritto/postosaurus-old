import re
import lamson.queue as queue
from webapp.postosaurus.models import *


def enqueue(message):
    """
    Message is the final version of the email sent
    to the entire group.
    """
    links_q = queue.Queue("run/links")
    links_q.push(message)


def add_link(list_addr, url):
    #todo: actually write this, this is pseudo code.
    if not_added(list_addr, url):
        l = Link()
        l.save

def not_added(list_addr, url):
    # do some sort of fancy query with django orm to find
    # a link with the given email list and url.
    pass

def extract_urls(body):
    crazy = "(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
    return re.findall(crazy, body)


