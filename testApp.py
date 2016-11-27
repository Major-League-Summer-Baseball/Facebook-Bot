'''
@author: Dallas Fraser
@date: 2016-11-26
@organization: Fun
@summary: Test the message responses
'''
import unittest
from app import parse_message, parse_meme, send_meme

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def callback(self, message, __):
        self.result = message
    def memeCallback(self, message, meme, __):
        self.message = message
        self.meme = meme
        send_meme(message, meme, "1369431089736367")

    def testBestMessage(self):
        parse_message("who the best", self.callback, "")
        self.assertEqual("Obviously the Maple Leafs", self.result)
        self.result = ""
        parse_message("who the not best", self.callback, "")
        self.assertNotEqual("Obviously the Maple Leafs", self.result)
        parse_message("Who the Best", self.callback, "")
        self.assertEqual("Obviously the Maple Leafs", self.result)
        parse_message("Who the Best hockey team", self.callback, "")
        self.assertEqual("Obviously the Maple Leafs", self.result)

    def testWouldYouRather(self):
        parse_message("Would you rather eat cake or  eat dirt?", self.callback, "")
        self.assertEqual(self.result in "eat cake eat dirt", True)
        parse_message("Would you Rather smoke weed or smoke cigs?", self.callback, "")
        self.assertEqual(self.result in "smoke weed smoke cigs", True)

    def testMeme(self):
        parse_meme("meme", self.memeCallback, "")
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()