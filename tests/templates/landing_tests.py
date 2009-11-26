import unittest
from django.test.client import Client

class LandingTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_response(self):
        response = self.client.get('/landing/')
        self.failUnlessEqual(response.status_code, 200)
