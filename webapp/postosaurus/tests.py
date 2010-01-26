import unittest
from postosaurus.models import *

class SpreedlyUpdate(unittest.TestCase):

    def setUp(self):
        pass

    def testUpdate(self):
        users = User.objects.all()
        
