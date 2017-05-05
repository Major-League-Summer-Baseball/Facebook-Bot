'''
Created on May 3, 2017

@author: Dallas
'''
import unittest
import sys
from json import loads as loader


def loads(data):
    try:
        data = loader(data)
    except:
        data = loader(data.decode('utf-8'))
    return data


def log(message):
    # simple wrapper for logging to stdout on heroku
    try:
        print(str(message))
        sys.stdout.flush()
    except Exception as e:
        print(str(e))
        pass


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
