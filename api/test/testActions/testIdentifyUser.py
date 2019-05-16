'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test helper functions
'''
from api.messenger.user import User
from api.message import Message
from api.test.testActions import TestActionBase
from api.test.testDoubles import MessengerStub, MongoStub, PlatformStub
from api.actions.identify_user import IdentifyUser
from api.actions.action_map import ACTION_MAP
from api.variables import IDENTIFY_KEY, WELCOME_KEY
import unittest


class TestIdentifyUser(TestActionBase):

    def setUp(self):
        super(TestIdentifyUser, self).setUp()

    def testFirstMessageDoNotMatch(self):
        """
        Test that upon a first message and do not match based upon messenger
        email or messenger name that we ask for their email.
        """

        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email="TestEmail@mlsb.ca",
                    gender="M")
        self.messenger.set_mock_user(user=user)
        message = Message(test_sender_id, message="Hey what is up")

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(ACTION_MAP)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), IDENTIFY_KEY)
        self.assertEqual(action_state.get_data(), {'wrongGuesses': 0})
        self.assertEqual(action_state.get_state(), IdentifyUser.EMAIL_STATE)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

    def testFirstMessageMatchEmail(self):
        """
        Test that upon a first message and match upon email that we will
        welcome to the league.
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email="TestEmail@mlsb.ca",
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the platform will recognize the player by email
        test_player_info = {"player_id": 1}
        self.platform.set_mock_player(player_by_email=test_player_info)

        # got the message what is up
        message = Message(test_sender_id, message="Hey what is up")

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(ACTION_MAP)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected, welcome state
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), WELCOME_KEY)
        self.assertEqual(action_state.get_data(), {})
        self.assertEqual(action_state.get_state(), None)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

        # make player info was saved
        self.assertEqual(save_player.get_player_id(), 1)
        self.assertEqual(save_player.get_player_info(), test_player_info)

    def testFirstMessageMatchName(self):
        """
        Test that upon a first message and match upon person name that we will
        welcome to the league.
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email=None,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the platform will recognize the player by email
        test_player_info = {"player_id": 1}
        self.platform.set_mock_player(player_by_name=test_player_info)

        # got the message what is up
        message = Message(test_sender_id, message="Hey what is up")

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(ACTION_MAP)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected, welcome state
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), WELCOME_KEY)
        self.assertEqual(action_state.get_data(), {})
        self.assertEqual(action_state.get_state(), None)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

        # make player info was saved
        self.assertEqual(save_player.get_player_id(), 1)
        self.assertEqual(save_player.get_player_info(), test_player_info)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
