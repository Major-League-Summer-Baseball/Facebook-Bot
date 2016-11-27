'''
Created on Nov 26, 2016

@author: Dallas
'''

import requests
import re
from random import randint

def meme_response(message, callback, id):
    message = message.lower()
    if re.search(r"(meme)+", message):
        r = requests.get("http://version1.api.memegenerator.net/Generators_Select_ByTrending")
        if r.status_code == 200:
            meme = r.json()['result']
            meme = meme[randint(0, len(meme) - 1)]
            print(meme)
            callback(meme['displayName'], meme['imageUrl'], id)

import pprint
import unittest
class Test(unittest.TestCase):

    def setUp(self):
        self.pp = pprint.PrettyPrinter(indent=4)

    def tearDown(self):
        pass

    def callback(self, message, memeUrl, __):
        self.result = message
        self.pp.pprint(self.result)

    def testMeme(self):
        meme_response("meme", self.callback, id)
        self.pp.pprint(self.result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()