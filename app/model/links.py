import re
import lamson.queue as queue
from webapp.postosaurus.models import *
from app.model import mailinglist


# This is some crazy regular expression I found on the internets for validating a url.
crazy = "(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"


# This is my dead simple regular expression for extracting urls. I run this first and then check it against
# the crazy regular expression.   
findurls = """
[\n\b"\(,]+                 # urls must be enclosed in quotes, parenthesis, commas, or word breaks
(?:(?:.+://)?(?:www\.)?){1,2}     # Anything like http:// and www is accepted, but optional. At least one required.
[\n\b"\),]+                 # closing boundary
"""

findurls = """
\s((?:.+://)(?:www\.))
"""


def add_link(list_name, url, message):
    mlist = mailinglist.find_list(list_name)
    if not_added(mlist, url):
        link = Link(mlist=mlist, url=url, message=message)
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


def extract_urls_from_text(body):
    
    candidates = re.findall(findurls, body, re.VERBOSE)
    print candidates
    print body
    urls = []
    for url in candidates:
        if re.match(crazy, url):
            urls.append(url)

    return urls


