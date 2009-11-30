from nose import with_setup
from webapp.postosaurus.models import *
from app.model import files, mailinglist, archive
from lamson.mail import MailRequest
from config import settings
import os
import shutil
import re

host = "postosaurus.com"
list_name = "test.list"
list_addr = "%s@%s" % (list_name, host)
sender = "send <sender@sender.com>"
member = "member <member@member.com>"

deneen_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/deneen-attachment.msg").read())
text_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/text-attachment.msg").read())
two_msg = MailRequest('fakeperr', sender, list_addr, open("tests/data/two-attachments.msg").read())


def setup_func():
    mlist = MailingList(name = list_name, email = list_addr)
    mlist.save()
    if os.path.isdir(settings.FILES_DIR):
        shutil.rmtree(settings.FILES_DIR)
    os.mkdir(settings.FILES_DIR)


def teardown_func():
    # clear the database
    MailingList.objects.all().delete()
    User.objects.all().delete()


@with_setup(setup_func, teardown_func)
def test_get_file_text():

    """
    Gets the text from the attached file.
    """
    
    text = files.file_text(text_msg, "customerinterviews.txt")
    assert len(re.findall("Next step for us", text)) > 0


@with_setup(setup_func, teardown_func)
def test_file_names():
    
    """
    Gets the names of each attachment attached to an email.
    """

    names = files.file_names(text_msg)
    assert len(names) == 1
    assert names[0] == "customerinterviews.txt"

    names = files.file_names(two_msg)
    assert len(names) == 2
    assert names[0] == "sean-text.txt"
    assert names[1] == "bfioritto_tutoring_reflection.doc"


@with_setup(setup_func, teardown_func)
def test_store_files():
    
    """
    Stores a file in the file system and creates a database record.
    """

    user = mailinglist.create_user(text_msg['from'])
    dbmessage = archive.store_message(list_name, text_msg)
    dbfile = files.store_file(list_name, text_msg, "customerinterviews.txt", dbmessage)
    assert dbfile.name == "customerinterviews.txt"

    user = mailinglist.create_user(two_msg['from'])
    dbmessage = archive.store_message(list_name, two_msg)
    dbfile = files.store_file(list_name, two_msg, "sean-text.txt", dbmessage)
    assert dbfile.name == "sean-text.txt"

