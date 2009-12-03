from nose.tools import *
from app.model.confirm import *
from config import settings, testing
from webapp.postosaurus.models import *
from lamson.testing import *
from lamson import mail, queue
import shutil
import os


def setup():
    mlist = MailingList(name = 'confirmtest',
                        email = 'confirmtest@postosaurus.com')
    mlist.save()

def teardown():
    MailingList.objects.all().delete()
    JoinConfirmation.objects.all().delete()
    if os.path.exists('run/queue'):
        shutil.rmtree('run/queue')

teardown()

storage = JoinConfirmStorage()
engine = ConfirmationEngine(storage)

def test_ConfirmationStorage():
    mlist = MailingList.objects.filter(name='confirmtest').all()[0]

    storage.store(mlist, 'testing', 'somedude@localhost', '12345')

    secret = storage.get(mlist, 'testing', 'somedude@localhost')
    assert_equal(secret, '12345')

    storage.delete(mlist, 'testing', 'somedude@localhost')
    assert_equal(len(storage.confirmations()), 0)

    storage.store(mlist, 'testing', 'somedude@localhost', '12345')
    assert_equal(len(storage.confirmations()), 1)
    storage.clear()
    assert_equal(len(storage.confirmations()), 0)


def test_ConfirmationEngine_send():
    if os.path.exists('run/queue'):
        shutil.rmtree('run/queue')
    engine.clear()
    mlist = MailingList.objects.filter(name='confirmtest').all()[0]
    action = 'subscribing to'
    host = 'localhost'
    from config import settings
    engine.send(settings.relay, mlist, 'confirm', 'somedude@localhost', 'postosaurus/join-confirmation.msg', host)
   
    confirm = delivered('confirm')
    assert confirm

    target, _, expect_secret = confirm['Reply-To'].split('-')
    expect_secret = expect_secret.split('@')[0]
    secrets = [c.secret for c in JoinConfirmation.objects.all()]
    assert expect_secret in secrets, "%s not in %s" % (expect_secret, secrets)

    return confirm


def test_ConfirmationEngine_verify():

    confirm = test_ConfirmationEngine_send()
    mlist = MailingList.objects.filter(name='confirmtest').all()[0]
    
    resp = mail.MailRequest('fakepeer', '"Somedude Smith" <somedude@localhost>',
                           confirm['Reply-To'], 'Fake body')
    listname, target, expect_secret = confirm['Reply-To'].split('-')
    expect_secret = expect_secret.split('@')[0]

    found = engine.verify(mlist, target, resp['from'], 'invalid_secret')
    assert not found

    pending = engine.verify(mlist, target, resp['from'], expect_secret)

    assert pending, "Verify failed: %r not in %r." % (expect_secret,
                                                      [c.secret for c in storage.confirmations()])


def test_ConfirmationEngine_cancel():
    confirm = test_ConfirmationEngine_send()
    mlist = MailingList.objects.filter(name='confirmtest').all()[0]

    target, _, expect_secret = confirm['Reply-To'].split('-')
    expect_secret = expect_secret.split('@')[0]

    engine.cancel(mlist, target, confirm['To'], expect_secret)
    
    found = engine.verify(mlist, target, confirm['To'], expect_secret)
    assert not found
