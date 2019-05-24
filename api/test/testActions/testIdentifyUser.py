'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test Identify User Action
'''
from api.test.testDoubles import NoAction
from api.messenger.user import User
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions.identify_user import IdentifyUser
from api.settings.action_keys import IDENTIFY_KEY, WELCOME_KEY
from api.settings.message_strings import ASK_FOR_EMAIL, WELCOME_LEAGUE,\
    IMPOSTER, LOCKED_OUT

import unittest


class TestIdentifyUser(TestActionBase):

    def setUp(self):
        self.action_map = {WELCOME_KEY: NoAction}
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
        identify.process(self.action_map)

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

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(ASK_FOR_EMAIL, message.get_message())

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
        identify.process(self.action_map)

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

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(WELCOME_LEAGUE.format(test_sender_name),
                         message.get_message())

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
        identify.process(self.action_map)

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

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(WELCOME_LEAGUE.format(test_sender_name),
                         message.get_message())

    def testFirstMessageImposter(self):
        """
        Test that upon a first message and the person email / name seems to
        indicate that they already are using the messenger that
        we ask for their email.
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email=None,
                    gender="M")
        self.messenger.set_mock_user(user=user)
        self.db.set_already_in_league(True)

        # the platform will recognize the player by email
        test_player_info = {"player_id": 1}
        self.platform.set_mock_player(player_by_name=test_player_info)

        # got the message what is up
        message = Message(test_sender_id, message="Hey what is up")

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(self.action_map)

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

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(ASK_FOR_EMAIL, message.get_message())

    def testMessageWithTheirEmailButImposter(self):
        """
        Test that upon a message with an email that is already claim by some
        other user of the bot.
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_email = "testMessageWithTheirEmailButImposted@mlsb"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email=test_email,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the player is already in the league
        self.db.set_already_in_league(True)
        player = Player(messenger_id=test_sender_id, name=test_sender_name)

        # set the state to such that we are expecting their email
        action_state = player.get_action_state()
        action_state.set_state(IdentifyUser.EMAIL_STATE)
        action_state.set_data({"wrongGuesses": 0})
        player.set_action_state(action_state)

        # set the db to return this player
        self.db.set_player(player)

        # we match the player on the platform
        test_player_info = {"player_id": 1}
        self.platform.set_mock_player(player_by_email=test_player_info)

        # got the message contain their email
        message = "My email is {}".format(test_email)
        message = Message(test_sender_id, message=message)

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), IDENTIFY_KEY)
        self.assertEqual(action_state.get_data(), {'wrongGuesses': 0})
        self.assertEqual(action_state.get_state(), IdentifyUser.IMPOSTER_STATE)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(IMPOSTER, message.get_message())

    def testMessageWithTheirEmailLockedOut(self):
        """
        Test when some user reponds with an email that
        they are locked out if they reached the max number of guesses
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_email = "testMessageWithTheirEmailLockedOut@mlsb"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email=test_email,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the player is already in the league
        self.db.set_already_in_league(True)
        player = Player(messenger_id=test_sender_id, name=test_sender_name)

        # set the state to such that we are expecting their email
        action_state = player.get_action_state()
        action_state.set_state(IdentifyUser.EMAIL_STATE)
        action_state.set_data({"wrongGuesses": 3})
        player.set_action_state(action_state)

        # set the db to return this player
        self.db.set_player(player)

        # got the message contain their email
        message = "My email is {}".format(test_email)
        message = Message(test_sender_id, message=message)

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), IDENTIFY_KEY)
        self.assertEqual(action_state.get_data(), {'wrongGuesses': 4})
        self.assertEqual(action_state.get_state(),
                         IdentifyUser.LOCKED_OUT_STATE)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[-1]
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(LOCKED_OUT, message.get_message())

    def testMessageWithTheirEmailSuccessful(self):
        """
        Test when a user responds with an email that is unclaimed
        they are welcomed to the league.
        """
        # setup the user who is asking
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_email = "testMessageWithTheirEmailSuccessful@mlsb"
        user = User(test_sender_id,
                    name=test_sender_name,
                    email=test_email,
                    gender="M")
        self.messenger.set_mock_user(user=user)

        # the player associated with the messenger id
        player = Player(messenger_id=test_sender_id, name=test_sender_name)

        # set the state to such that we are expecting their email
        action_state = player.get_action_state()
        action_state.set_state(IdentifyUser.EMAIL_STATE)
        action_state.set_data({"wrongGuesses": 0})
        player.set_action_state(action_state)

        # set the db to return this player
        self.db.set_player(player)

        self.platform.set_mock_player(player_by_email={"player_id": 1})

        # got the message contain their email
        message = "My email is {}".format(test_email)
        message = Message(test_sender_id, message=message)

        # create the action and process the message
        identify = self.create_action(IdentifyUser, message)
        identify.process(self.action_map)

        # get the player object that was saved after action
        save_player = self.db.inspect_saved_player()

        # check the state is as expected
        action_state = save_player.get_action_state()
        self.assertEqual(action_state.get_id(), WELCOME_KEY)
        self.assertEqual(action_state.get_data(), {})
        self.assertEqual(action_state.get_state(),
                         None)

        # check the name and sender id were recorded properly
        self.assertEqual(
            test_sender_id, save_player.to_dictionary()['messenger_id'])
        self.assertEqual(test_sender_name, save_player.to_dictionary()[
                         'messenger_name'])

        # make sure the message sent back makes sense
        message = self.messenger.get_messages()[0]
        expected_message = WELCOME_LEAGUE.format(test_sender_name)
        self.assertEqual(test_sender_id, message.get_sender_id())
        self.assertEqual(None, message.get_payload())
        self.assertEqual(expected_message, message.get_message())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
