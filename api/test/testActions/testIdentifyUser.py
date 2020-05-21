'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test Identify User Action
'''
from api.test.testDoubles.noAction import Nop
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions import ActionKey
from api.actions.action.identify_user import IdentifyUser
from api.settings.message_strings import Registration
import unittest


class TestIdentifyUser(TestActionBase):
    TEST_SENDER_ID = "test welcome sender id"
    TEST_SENDER_NAME = "test welcome sender name"

    def setUp(self):
        self.action_map = {ActionKey.WELCOME_KEY: Nop}
        super(TestIdentifyUser, self).setUp()
        self.action = self.create_action(IdentifyUser)
        self.player = Player(messenger_id=TestIdentifyUser.TEST_SENDER_ID,
                             name=TestIdentifyUser.TEST_SENDER_NAME)
        player_info = self.random_player()
        self.player.set_player_info(player_info)

    def testFirstMessage(self):
        """Test when they just sent their first message"""
        # got the message contain their email and process the message
        message = "What is up my friend?"
        message = Message(TestIdentifyUser.TEST_SENDER_ID, message=message)
        player = Player(messenger_id=TestIdentifyUser.TEST_SENDER_ID,
                        name=TestIdentifyUser.TEST_SENDER_NAME)
        (player, messages, next_action) = self.action.process(player,
                                                              message)

        # should have been prompted for email
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          Registration.EMAIL_PROMPT.value)

        # state should be set accordingly
        action_state = player.get_action_state()
        self.assertEqual(action_state.get_id(), ActionKey.IDENTIFY_KEY)
        self.assertEqual(action_state.get_state(), IdentifyUser.EMAIL_STATE)

        # ensure no next action is taken
        self.assertIsNone(next_action)

    def testMissingEmailMessage(self):
        """Test when the message has not email"""
        # set the state to such that we are expecting their email response
        state = IdentifyUser.EMAIL_STATE
        self.player.set_action_state(self.player
                                     .get_action_state()
                                     .set_state(state))

        # send message with no email
        email = "I do not know"
        message = Message(TestIdentifyUser.TEST_SENDER_ID, message=email)
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          Registration.EMAIL_PROMPT.value)

        # ensure no next action is taken
        self.assertIsNone(next_action)

    def testCatchingImposter(self):
        """Test player using an already claimed email by another user."""
        # the player is already in the league
        self.db.set_already_in_league(True)

        # set the state to such that we are expecting their email
        state = IdentifyUser.EMAIL_STATE
        self.player.set_action_state(self.player
                                     .get_action_state()
                                     .set_state(state))

        # we match the player on the platform
        test_player_info = self.random_player()
        self.platform.set_mock_player(player_by_email=test_player_info)

        # got the message contain their email and process the message
        message = "My email is {}".format("someEmail@mlsb.ca")
        message = Message(TestIdentifyUser.TEST_SENDER_ID, message=message)
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)

        # check the state is as expected
        action_state = player.get_action_state()
        self.assertEqual(action_state.get_id(), ActionKey.IDENTIFY_KEY)
        self.assertEqual(action_state.get_state(), IdentifyUser.IMPOSTER_STATE)

        # make sure the message sent back makes sense
        message = messages[0]
        self.assertEqual(TestIdentifyUser.TEST_SENDER_ID,
                         message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(Registration.IMPOSTER.value, message.get_message())

        # ensure no next action is taken
        self.assertIsNone(next_action)

    def testEventuallyLockedOut(self):
        """Test that repeated guesses at an email eventually locks them out"""

        # set the state to such that we are expecting their email response
        state = IdentifyUser.EMAIL_STATE
        self.player.set_action_state(self.player
                                     .get_action_state()
                                     .set_state(state))

        # send a bunch of bad emails
        attempts = 0
        player = self.player
        while attempts <= IdentifyUser.NUMBER_OF_TRIES:

            email = "My email is {}".format(self.random_email())
            message = Message(TestIdentifyUser.TEST_SENDER_ID, message=email)
            (player, messages, next_action) = self.action.process(player,
                                                                  message)
            self.assertIsNone(next_action)
            self.assertEquals(len(messages), 2)
            self.assertEquals(messages[0].get_message(),
                              Registration.EMAIL_NOT_FOUND.value)
            self.assertEquals(messages[1].get_message(),
                              Registration.EMAIL_PROMPT.value)
            attempts += 1

        # ask one more time to get locked out
        email = "My email is {}".format(self.random_email())
        message = Message(TestIdentifyUser.TEST_SENDER_ID, message=email)
        (player, messages, next_action) = self.action.process(player,
                                                              message)
        # should be locked out
        action_state = player.get_action_state()
        self.assertEqual(action_state.get_id(), ActionKey.IDENTIFY_KEY)
        self.assertEqual(action_state.get_state(),
                         IdentifyUser.LOCKED_OUT_STATE)

        # make sure the message sent back makes sense
        message = messages[0]
        self.assertEquals(len(messages), 2)
        self.assertEquals(messages[0].get_message(),
                          Registration.EMAIL_NOT_FOUND.value)
        self.assertEqual(messages[1].get_message(),
                         Registration.LOCKED_OUT.value)

        # ensure no next action is taken
        self.assertIsNone(next_action)

    def testMessageWithTheirEmailSuccessful(self):
        """Test when they give a correct email that is not being used."""
        # the player has not signed up yet
        self.db.set_already_in_league(False)
        player_info = self.random_player()
        self.platform.set_mock_player(player_by_email=player_info)

        # set the state to such that we are expecting their email
        state = IdentifyUser.EMAIL_STATE
        self.player.set_action_state(self.player
                                     .get_action_state()
                                     .set_state(state))

        # got the message contain their email and process the message
        message = "My email is {}".format("someEmail@mlsb.ca")
        message = Message(TestIdentifyUser.TEST_SENDER_ID, message=message)
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)

        # ensure that the player info is saved
        self.assertEquals(player_info, player.get_player_info())

        # make sure that no message sent back (handles by welcome action)
        self.assertEquals(len(messages), 0)

        # ensure no next action is taken
        self.assertEquals(next_action, ActionKey.WELCOME_KEY)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
