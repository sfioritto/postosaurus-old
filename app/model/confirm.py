import uuid
from lamson import queue, view
from email.utils import parseaddr
from webapp.postosaurus.models import JoinConfirmation


class JoinConfirmStorage(object):

    def clear(self):

        """
        This is only used for testing.
        """

        JoinConfirmation.objects.all().delete()


    def get(self, mlist, target, address):
        confirmations = JoinConfirmation.objects.filter(address=address, 
                                                        mlist=mlist,
                                                        target=target)
        if confirmations:
            return confirmations[0].secret
        else:
            return None


    def delete(self, mlist, target, address):
        JoinConfirmation.objects.filter(address=address, 
                                        mlist=mlist,
                                        target=target).delete()


    def store(self, mlist, target, address, secret):
        conf = JoinConfirmation(address=address,
                                secret = secret,
                                target=target,
                                mlist=mlist)
        conf.save()

    
    def confirmations(self):
        return JoinConfirmation.objects.all()


class ConfirmationEngine(object):

    def __init__(self, storage):

        """
        Storage should be something that is like JoinConfirmStorage so that this
        can store things for later verification.
        """

        self.storage = storage


    def cancel(self, mlist, target, address, expect_secret):

        """
        Used to cancel a pending confirmation.
        """

        name, addr = parseaddr(address)

        secret = self.storage.get(mlist, target, addr)

        if secret == expect_secret:
            self.storage.delete(mlist, target, addr)


    def make_random_secret(self):

        """
        Generates a random uuid as the secret, in hex form.
        """

        return uuid.uuid4().hex


    def register(self, mlist, target, address):

        """
        Don't call this directly unless you know what you are doing.
        """

        secret = self.make_random_secret()
        self.storage.store(mlist, target, address, secret)

        return "%s-confirm-%s" % (target, secret)


    def verify(self, mlist, target, address, guess):

        assert guess, "Must give an expected ID number."
        name, addr = parseaddr(address)

        secret = self.storage.get(mlist, target, addr)

        if secret == guess:
            self.storage.delete(mlist, target, addr)
            return True
        else:
            return False


    def send(self, relay, mlist, target, message, template, vars):
        
        address = message.route_from
        confirm = self.register(mlist, target, address)
        vars.update(locals())
        msg = view.respond(vars, template, To=message['from'],
                           From="%(confirm)s@%(host)s",
                           Subject="Confirmation required")
        msg['Reply-To'] = "%(confirm)s@%(host)s" % vars

        relay.deliver(msg)


    def clear(self):

        """
        Used in testing to make sure there's nothing in the pending
        queue or storage.
        """

        self.storage.clear()
