'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a base class that setups some common things needed
'''
from api.test.testDoubles.messengerDouble import MessengerDouble
from api.test.testDoubles.databaseDouble import DatabaseDouble
from api.test.testDoubles.platformDouble import PlatformDouble
import unittest


class TestActionBase(unittest.TestCase):
    """Base Test Action"""

    def setUp(self):
        """Setups all the test doubles"""
        self.db = DatabaseDouble()
        self.platform = PlatformDouble()
        self.messenger = MessengerDouble()

    def create_action(self, action_class):
        """Will commonly need to create actions"""
        return action_class(self.db,
                            self.platform,
                            self.messenger)
