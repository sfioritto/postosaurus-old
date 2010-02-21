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


def create_hash_from_msg(message, filetext):
    
    """
    Returns the sha1 hash of the attached file.
    """

    return hashlib.sha1(filetext).hexdigest()

def create_hash_from_file(file):
    
    """
    This could potentially overwhelm the server's memory
    if the file is too big.
    """
    
    text = ""
    for chunk in file.chunks():
        text = text + chunk

    return hashlib.sha1(text).hexdigest()


def get_file_name(file):
    return os.path.basename(file.name)


def store_file(user, mlist, org, file):

    sha = create_hash_from_file(file)
    filename = get_file_name(file)

    dbfile = create_dbfile(mlist, user, sha, org, filename, os.path.splitext(filename)[1])
    dbfile.save()

    destination = get_destination(dbfile)
    
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    write_symlink(dbfile)


def find_dbfile(sha):

    try:
        return File.objects.get(sha=sha)
    except File.DoesNotExist:
        return None

def create_dbfile(mlist, user, sha, org, name, ext, message=None):

    dbfile = find_dbfile(sha)
    if not dbfile:
        dbfile = File(mlist = mlist,
                      message = message,
                      user = user,
                      sha = sha,
                      organization = org,
                      name = name,
                      ext = os.path.splitext(name)[1])
        dbfile.save()
    return dbfile
    


def get_destination(dbfile):

    """
    Given a file model object opens a file to store the file on the file system. Creates
    directores if necessary.
    """

    try:
        # try to just open the file and create it, assumes the directories already
        # exist, which they may not.
        destination = open(dbfile.local_path(), 'w')

    except IOError:
        # The directories haven't been created yet, go
        # through and make 'em.

        path = "/"
        for part in dbfile.local_path().split("/")[1:-1]:
            path = os.path.join(path, part)
            if not os.path.isdir(path):
                os.mkdir(path)

        #try again. Code duplicated to avoid performance hit checking to see if directory exists every
        #single time. This only needs to be done once per group.
        destination = open(dbfile.local_path(), 'w')

    return destination



def store_file_from_message(list_name, org, message, filename, dbmessage):

    """
    Given a list name and a filename store the attached file
    in the filesystem and create a db record to track relationships,
    (like this file was sent with this message, etc).
    """

    mlist = mailinglist.find_list(list_name, org.subdomain)
    name, addr = parseaddr(message['from'])
    user = mailinglist.find_user(addr)
    filetext = file_text(message, filename)
    sha = create_hash_from_msg(message, filetext)
    dbfile = create_dbfile(mlist, user, sha, org, filename, os.path.splitext(filename)[1], message=dbmessage)
    dbfile.save()

    destination = get_destination(dbfile)
    destination.write(file_text(message, filename))
    destination.close()
    
    write_symlink(dbfile)

    return dbfile


def write_symlink(dbfile):
    if os.path.islink(dbfile.recent_local_path()):
        os.remove(dbfile.recent_local_path())
    os.symlink(os.path.join(dbfile.sha, dbfile.name), dbfile.recent_local_path())
    
        
    
