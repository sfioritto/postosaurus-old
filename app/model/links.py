import re
import lamson.queue as queue
from webapp.postosaurus.models import *
from app.model import mailinglist


def enqueue(message):
    """
    Message is the final version of the email sent
    to the entire group.
    """
    links_q = queue.Queue("run/links")
    links_q.push(message)


def add_link(list_name, url):
    mlist = mailinglist.find_list(list_name)
    if not_added(mlist, url):
        link = Link(mlist=mlist, url=url)
        link.save()


def not_added(mlist, url):
    
    """
    Return true if the url provided has not already
    been added to the given mailing list.
    """

    links = Link.objects\
        .filter(mlist__id = mlist.id)\
        .filter(url=url).all()
    if len(links) > 0:
        # url was already added
        return False
    else:
        # url has not been added
        return True

    
def extract_urls_from_html(html):
    return []

def extract_urls_from_text(body):
    crazy = "(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
    return re.findall(crazy, body)


