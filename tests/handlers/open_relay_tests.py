from nose.tools import *
from lamson.testing import *
from lamson import server

relay = relay(port=8823)
domain = 'postosaurus.com'
sender = 'somedude@somedude.com'
client = RouterConversation(sender, "requests_tests")


def test_drops_open_relay_messages():
    """
    Make sure that mail NOT for postosaurus.com gets dropped silently.
    """
    client.begin()
    client.say("tester@badplace.notinterwebs", "Relay should not happen")
    assert queue().count() == 0, "Should not deliver that message."

