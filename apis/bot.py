'''
Created on Dec 2, 2016

@author: d6fraser
'''
import unittest

def da_bot_response(message, callback, id, bot):
    print(bot.get_response(message))


try:
    import sys
    sys.path.append("..") # Adds higher directory to python modules path.
    from config import URI
except:
    import os
    URI = os.environ['URI']
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

class Test(unittest.TestCase):

    def setUp(self):
        self.DA_BOT = ChatBot("ResumeBot",
                              storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                              database=URI)
        self.DA_BOT.set_trainer(ChatterBotCorpusTrainer)
        self.DA_BOT.train("chatterbot.corpus.english")


    def tearDown(self):
        pass

    def callback(self, message, __):
        print(message)

    def testBot(self):
        da_bot_response("Hey", self.callback, "1", self.DA_BOT)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()