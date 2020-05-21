'''
@author: Dallas Fraser
@author: 2020-05-10
@organization: MLSB
@project: Facebook Bot
@summary: Test the action processor
'''
from api.test.testDoubles.noAction import Nop
from api.messenger.user import User
from api.message import Message
from api.test.testActions import TestActionBase
from api.actions.action_processor import ActionProcessor
from api.actions import ActionKey
from api.actions.action.identify_user import IdentifyUser
from api.settings.message_strings import Registration

import unittest


class TestActionProcessor(TestActionBase):
    TEST_SENDER_ID = "test action processor sender id"
    TEST_SENDER_NAME = "test action processor sender id"
    TEST_EMAIL = "TestEmail@mlsb.ca"

    def setUp(self):
        self.action_map = {ActionKey.IDENTIFY_KEY: IdentifyUser,
                           ActionKey.WELCOME_KEY: Nop}
        super(TestActionProcessor, self).setUp()
        self.processor = ActionProcessor(self.db, self.platform,
                                         self.messenger)

    def testFirstMessageDoNotMatch(self):
        """Test first message but can't recongize them from messenger infor."""

        # setup the user who is asking
        user = User(TestActionProcessor.TEST_SENDER_ID,
                    name=TestActionProcessor.TEST_SENDER_NAME,
                    email=TestActionProcessor.TEST_EMAIL,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # got the message what is up and process the action
        message = Message(TestActionProcessor.TEST_SENDER_ID,
                          message="Hey what is up")
        self.processor.process(message, self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected
        self.assertEqual(save_player.get_action_state().get_id(),
                         ActionKey.IDENTIFY_KEY)

        # check the name and sender id were recorded properly
        self.assertEqual(TestActionProcessor.TEST_SENDER_ID,
                         save_player.to_dictionary()['messenger_id'])
        self.assertEqual(TestActionProcessor.TEST_SENDER_NAME,
                         save_player.to_dictionary()['messenger_name'])

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(TestActionProcessor.TEST_SENDER_ID,
                         message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(Registration.EMAIL_PROMPT.value,
                         message.get_message())

    def testFirstMessageMatchEmail(self):
        """Test the first message matches their messenger email."""
        # setup the user who is asking
        user = User(TestActionProcessor.TEST_SENDER_ID,
                    name=TestActionProcessor.TEST_SENDER_NAME,
                    email=TestActionProcessor.TEST_EMAIL,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the platform will recognize the player by email
        test_player_info = self.random_player()
        self.platform.set_mock_player(player_by_email=test_player_info)

        # got the message what is up and process the action
        message = Message(TestActionProcessor.TEST_SENDER_ID,
                          message="Hey what is up")
        self.processor.process(message, self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected, welcome state
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), ActionKey.WELCOME_KEY)

        # check the name and sender id were recorded properly
        self.assertEqual(TestActionProcessor.TEST_SENDER_ID,
                         save_player.to_dictionary()['messenger_id'])
        self.assertEqual(TestActionProcessor.TEST_SENDER_NAME,
                         save_player.to_dictionary()['messenger_name'])

        # check player info was saved
        self.assertEqual(save_player.get_player_id(),
                         test_player_info.get("player_id"))
        self.assertEqual(save_player.get_player_info(), test_player_info)

        # expecting no message since using a NOP for welcome
        self.assertEquals(0, len(self.messenger.get_messages()))

    def testFirstMessageMatchName(self):
        """Test the first message matches their messenger name."""
        # setup the user who is asking
        user = User(TestActionProcessor.TEST_SENDER_ID,
                    name=TestActionProcessor.TEST_SENDER_NAME,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the platform will recognize the player by name
        test_player_info = self.random_player()
        self.platform.set_mock_player(player_by_name=test_player_info)

        # got the message what is up and process the action
        message = Message(TestActionProcessor.TEST_SENDER_ID,
                          message="Hey what is up")
        self.processor.process(message, self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected, welcome state
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), ActionKey.WELCOME_KEY)

        # check the name and sender id were recorded properly
        self.assertEqual(TestActionProcessor.TEST_SENDER_ID,
                         save_player.to_dictionary()['messenger_id'])
        self.assertEqual(TestActionProcessor.TEST_SENDER_NAME,
                         save_player.to_dictionary()['messenger_name'])

        # check player info was saved
        self.assertEqual(save_player.get_player_id(),
                         test_player_info.get("player_id"))
        self.assertEqual(save_player.get_player_info(), test_player_info)

        # expecting no message since using a NOP for welcome
        self.assertEquals(0, len(self.messenger.get_messages()))


if __name__ == "__main__":
    unittest.main()
