import unittest
from pymdc.rest import REST

class TestRest(unittest.TestCase):
    def test_rest(self):
        self.assertTrue(type(REST("GET", "/")) == dict)
