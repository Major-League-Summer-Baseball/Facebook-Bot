'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Welcome Action
'''
from api.helper import get_this_year
from api.test.testDoubles.noAction import NoAction
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions.welcome import WelcomeAction
from api.settings.action_keys import HOME_KEY
from api.settings.message_strings import PART_OF_TEAM, ACKNOWLEDGE_CAPTAIN,\
    ACKNOWLEDGE_CONVENOR
import unittest


class TestWelcome(TestActionBase):

    def setUp(self):
        self.action_map = {HOME_KEY: NoAction}
        super(TestWelcome, self).setUp()
        self.action = self.create_action(WelcomeAction)

    def testNormalPlayer(self):
        """
        Test welcoming a normal player
        """

        # some test data
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_player_id = 1
        test_team_name = "Test Team Name"
        test_team_id = 1
        test_teams = [{"year": get_this_year(),
                       "team_name": test_team_name,
                       "team_id": test_team_id,
                       "captain": {"player_id": test_player_id + 1}},
                      {"year": get_this_year() - 1,
                       "team_name": test_team_name + "2",
                       "team_id": test_team_id + 1,
                       "captain": {"player_id": test_player_id}}]
        message = Message(test_sender_id, message="")

        # setup the background of the player
        player = Player(messenger_id=test_sender_id, name=test_sender_name)
        player.set_player_info({"player_id": test_player_id})
        self.db.set_player(player)
        self.platform.set_mock_teams(teams=test_teams)

        # process the message
        self.action.process(message, self.action_map)

        # check if the expected messages were sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(player.get_team_ids(), [test_team_id])
        self.assertEqual(messages[0].get_message(),
                         PART_OF_TEAM.format(test_team_name))
        self.assertEqual(messages[0].get_sender_id(), test_sender_id)

        # make sure player was subscribed to team
        player = self.db.inspect_saved_player()
        self.assertTrue(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id))

        # but not subscribed to team from last year
        self.assertFalse(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id + 1))

        # check action state was updated
        self.assertEqual(player.get_action_state().get_id(), HOME_KEY)
        self.assertEqual(player.get_action_state().get_data(), {})

    def testCaptain(self):
        """
        Test welcoming a Captain player
        """
        # some test data
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_player_id = 1
        test_team_name = "Test Team Name"
        test_team_id = 1
        test_teams = [{"year": get_this_year(),
                       "team_name": test_team_name,
                       "team_id": test_team_id,
                       "captain": {"player_id": test_player_id}},
                      {"year": get_this_year() - 1,
                       "team_name": test_team_name + "2",
                       "team_id": test_team_id + 1,
                       "captain": {"player_id": test_player_id + 1}}]
        message = Message(test_sender_id, message="")

        # setup the background of the player
        player = Player(messenger_id=test_sender_id, name=test_sender_name)
        player.set_player_info({"player_id": test_player_id})
        self.db.set_player(player)
        self.platform.set_mock_teams(teams=test_teams)

        # process the message
        self.action.process(message, self.action_map)

        # check if the expected messages were sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(player.get_team_ids(), [test_team_id])
        self.assertEqual(messages[0].get_message(),
                         PART_OF_TEAM.format(test_team_name))
        self.assertEqual(messages[0].get_sender_id(), test_sender_id)
        self.assertEqual(messages[1].get_message(),
                         ACKNOWLEDGE_CAPTAIN)
        self.assertEqual(messages[1].get_sender_id(), test_sender_id)

        # make sure player was subscribed to team and is captain
        player = self.db.inspect_saved_player()
        self.assertTrue(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id))
        self.assertTrue(player.is_captain(team_id=test_team_id))

        # but not subscribed to team from last year
        self.assertFalse(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id + 1))

        # check action state was updated
        self.assertEqual(player.get_action_state().get_id(), HOME_KEY)
        self.assertEqual(player.get_action_state().get_data(), {})

    def testConvenor(self):
        """
        Test welcoming a convenor
        """

        # some test data
        test_sender_id = "test_sender_id"
        test_sender_name = "TestName"
        test_player_id = 1
        test_player_email = "TestEmail@mlsb.ca"
        test_team_name = "Test Team Name"
        test_team_id = 1
        test_teams = [{"year": get_this_year(),
                       "team_name": test_team_name,
                       "team_id": test_team_id,
                       "captain": {"player_id": test_player_id + 1}},
                      {"year": get_this_year(),
                       "team_name": test_team_name + "2",
                       "team_id": test_team_id + 1,
                       "captain": {"player_id": test_player_id}}]
        message = Message(test_sender_id, message="")

        # setup the background of the player
        player = Player(messenger_id=test_sender_id, name=test_sender_name)
        player.set_player_info({"email": test_player_email,
                                "player_id": test_player_id})
        self.db.set_convenors(["testEmail2@mlsb.ca",
                               test_player_email,
                               "testEmail2@mlsb.ca"])
        self.db.set_player(player)
        self.platform.set_mock_teams(teams=test_teams)

        # process the message
        self.action.process(message, self.action_map)

        # check if the expected messages were sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(player.get_team_ids(),
                         [test_team_id, test_team_id + 1])
        self.assertEqual(messages[0].get_message(),
                         ACKNOWLEDGE_CONVENOR)
        self.assertEqual(messages[0].get_sender_id(), test_sender_id)

        # make sure convenor is subscribed to all teams
        self.assertTrue(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id))
        self.assertTrue(player.get_subscriptions(
        ).is_subscribed_to_team(test_team_id + 1))

        # check action state was updated
        self.assertEqual(player.get_action_state().get_id(), HOME_KEY)
        self.assertEqual(player.get_action_state().get_data(), {})


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
