import os
import hashlib
from config import settings
from webapp.postosaurus.models import Message, File
from app.model import mailinglist
from email.utils import parseaddr


def file_text(message, filename):

    """
    Returns the text of the attached file in the message, which
    is hopefully not ridiculously huge...
    """

    part = get_part_with_file(message, filename)
    return part.body


def get_part_with_file(message, filename):
    
    """
    Returns the part with the given file in it.
    """
    
    for part in message.all_parts():
        key, values = part.content_encoding['Content-Disposition']
        if key == 'attachment' and values['filename'] == filename:
            return part
    return None


def file_names(message):

    """
    Returns a list of file names of files attached to the
    message.
    """
    
    encodings = [part.content_encoding['Content-Disposition'] for part in message.all_parts()]
    
    # each disposition is a tuple like ('attachment', {'filename', 'myfile.doc'})
    filenames = [values['filename'] for key, values in encodings if key == 'attachment']
    return filenames


def create_hash_from_msg(message, filename):
    
    """
    Returns the sha1 hash of the attached file.
    """

    text = file_text(message, filename)
    return hashlib.sha1(text).hexdigest()

    
def store_file(list_name, org, message, filename, dbmessage):

    """
    Given a list name and a filename store the attached file
    in the filesystem and create a db record to track relationships,
    (like this file was sent with this message, etc).
    """

    mlist = mailinglist.find_list(list_name, org)
    name, addr = parseaddr(message['from'])
    user = mailinglist.find_user(addr)
    sha = create_hash_from_msg(message, filename)
    dbfile = File(mlist = mlist,
                  message = dbmessage,
                  user = user,
                  sha = sha,
                  organization = org,
                  name = filename,
                  ext = os.path.splitext(filename)[1])
    dbfile.save()

    try:
        # try to just open the file and create it, assumes the directories already
        # exist, which they may not.
        pfile = open(dbfile.local_path(), 'w')
        pfile.write(file_text(message, filename))
        pfile.close()
    except IOError:
        # The directories haven't been created yet, go
        # through and make 'em.

        path = ""
        for part in dbfile.local_path().split("/")[:-1]:
            path = os.path.join(path, part)
            if not os.path.isdir(path):
                os.mkdir(path)

        #try again. Code duplicated to avoid performance hit checking to see if directory exists every
        #single time. This only needs to be done once per group.
        pfile = open(dbfile.local_path(), 'w')
        pfile.write(file_text(message, filename))
        pfile.close()
        
        if os.path.islink(dbfile.recent_local_path()):
            os.remove(dbfile.recent_local_path())
        os.symlink(os.path.join(dbfile.sha, dbfile.name), dbfile.recent_local_path())

    return dbfile

        
    
