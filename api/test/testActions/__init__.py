'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a base class that setups some common things needed
'''
from api.test.testDoubles import MessengerStub, MongoStub, PlatformStub
import unittest


class TestActionBase(unittest.TestCase):
    """Base Test Action"""

    def setUp(self):
        """Setups all the test doubles"""
        self.db = MongoStub()
        self.platform = PlatformStub()
        self.messenger = MessengerStub()

    def create_action(self, action_class, message):
        """Will commonly need to create actions"""
        return action_class(self.db,
                            self.platform,
                            self.messenger,
                            message)
