import unittest
from postosaurus.models import MailingList

class MailingListTestCase(unittest.TestCase):
    def setUp(self):
        self.list = MailingList(name="bob", email="bob")

    def testName(self):
        self.assertEquals(self.list.name, 'bob')

