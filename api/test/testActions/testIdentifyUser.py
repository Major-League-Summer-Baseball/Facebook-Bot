'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test helper functions
'''
from api.messenger.user import User
from api.test.testActions import TestActionBase
from api.test.testDoubles import MessengerStub, MongoStub, PlatformStub
from api.actions.identify_user import IdentifyUser
import unittest


class TestIdentifyUser(TestActionBase):

    def setUp(self):
        super(TestIdentifyUser, self).setUp()

    def testAskForEmail(self):
        """
        Test that when unable to find player based upon messenger
        so ask for email.
        """
        user = User("test_sender_id",
                    name="TestName",
                    email="TestEmail@mlsb.ca",
                    gender="M")
        self.messenger.set_mock_user(user)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
