from fabric.api import *

env.hosts = ['postosaurus.com']



def test():
    local("nosetests")


def pack(hash):

    """
    Creates a clean copy of the code
    """
    archivename = "%s.tar.gz" % hash
    local("git archive --format=tar %s | gzip > /tmp/%s;" % (hash, archivename))
    return archivename


def prepare(hash):

    """
    Test and archive postosaurus.
    """

    test()
    pack(hash)


def upload(archive):
    put('/tmp/%s' % archive, '/tmp/')


def untar(archive, hash):
    with settings(warn_only=True):
        with cd(env.prodhome):
            run("rm -rf snapshots/%s" % hash)
            run("mkdir snapshots/%s" % hash)
            run("cd snapshots/%s; tar -xvf '/tmp/%s'" % (hash,archive))


def upload_untar(archive, hash):
    upload(archive)
    untar(archive, hash)


def deploy(hash):
    with cd(env.devpath):
        test()
        archive = pack(hash)
    upload_untar(archive, hash)
    
    

