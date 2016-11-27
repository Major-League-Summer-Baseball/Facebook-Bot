'''
@author: Dallas Fraser
@date: 2016-11-26
@organization: Fun
@summary: Holds the api for if someone asks about trump
'''
import re
import requests
from random import randint

def trump_response(message, callback, id):
    message = message.lower()
    if re.search(r"(trump|donald)+", message):
        r = requests.get("https://api.whatdoestrumpthink.com/api/v1/quotes")
        if r.status_code == 200:
            r_object = r.json()
            print(r_object)
            if re.search(r"you(\s)*(think)+", message):
                upper_range = len(r_object['messages']['non_personalized']) - 1
                random_number = randint(0, upper_range)
                callback(r_object['messages']['non_personalized'][random_number], id)
            elif re.search(r"he(\s)*(say)+", message):
                upper_range = len(r_object['messages']['personalized']) - 1
                random_number = randint(0, upper_range)
                callback(r_object['messages']['personalized'][random_number], id)
            else:
                random_number = randint(0, 1)
                field = "non_personalized"
                if random_number == 0:
                    field = "personalized"
                random_number = randint(0, len(r_object['messages'][field]) - 1)
                callback(r_object['messages'][field][random_number], id)

import pprint
import unittest
class Test(unittest.TestCase):

    def callback(self, message, __):
        self.result = message

    def setUp(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        
    def tearDown(self):
        pass

    def testTrumpResponse(self):
        self.result = "no"
        trump_response("Trump is awesome", self.callback, "")
        self.assertNotEqual("no", self.result)
        self.pp.pprint(self.result)

    def testNonTrumpResponse(self):
        self.result = "no"
        trump_response("Hillary is awesome", self.callback, "")
        self.assertEqual("no", self.result)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()