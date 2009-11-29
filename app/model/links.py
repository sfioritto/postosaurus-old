import re
import lamson.queue as queue
from webapp.postosaurus.models import *
from app.model import mailinglist

#Adding a comment to test commit hook.
# This is some crazy regular expression I found on the internets for validating a url.
crazy = "(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"


# This is my 'simpler' regular expression for extracting urls. I run this first and then check it against
# the crazy regular expression.   
findurls = """
(?:^|[\^\n\s"\(,]+)                    # urls must be enclosed in quotes, parenthesis, commas, or word breaks
(                              # group the url
(?:\w+://)?                    # Anything like http:// is accepted, but optional.
(?:www)?                       # Optionally followed by www
(?:[^@.\s]+\.)+                # (Sub)domain(s)
(?:com|org|net|gov|mil|biz|    # Top level domains.
info|mobi|name|aero|jobs|
museum|travel|[a-z]{2}){1}
(?:\S+)?                            # Path to resource
)                              # end url group
(?:$|[\n\s"\),]+)                    # closing boundary
"""
#

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
    urls = []
    for url in candidates:
        if re.match(crazy, url):
            urls.append(url)

    return urls


