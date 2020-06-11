'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Welcome Action
'''
from api.helper import get_this_year
from api.test.testDoubles.noAction import Nop
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions import ActionKey
from api.actions.action.welcome import WelcomeUser
from api.settings.message_strings import Registration
import unittest


class TestWelcome(TestActionBase):
    TEST_SENDER_ID = "test welcome sender id"
    TEST_SENDER_NAME = "test welcome sender name"

    def setUp(self):
        self.action_map = {ActionKey.HOME_KEY: Nop}
        super(TestWelcome, self).setUp()
        self.action = self.create_action(WelcomeUser)

        # some test data
        player_info = self.random_player()

        # setup the background of the player
        self.player = Player(messenger_id=TestWelcome.TEST_SENDER_ID,
                             name=TestWelcome.TEST_SENDER_NAME)
        self.player.set_player_info(player_info)

    def testNormalPlayer(self):
        """Test welcoming a normal player"""

        # player is part of some teams
        test_teams = [self.random_team(),
                      self.random_team(year=get_this_year() - 1)]
        self.platform.lookup_teams_player_associated_with\
            .return_value = test_teams

        # process the message
        message = Message(TestWelcome.TEST_SENDER_ID)
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)

        # check if the expected messages were sent back
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].get_message(),
                         Registration.ON_TEAM.value.format(test_teams[0]
                                                           .get("team_name")))
        self.assertEqual(messages[1].get_sender_id(),
                         TestWelcome.TEST_SENDER_ID)

        # make sure player was subscribed to team
        self.assertEqual(player.get_team_ids(),
                         [test_teams[0].get("team_id")])
        self.assertTrue(player.get_subscriptions()
                        .is_subscribed_to_team(test_teams[0].get("team_id")))

        # but not subscribed to team from last year
        self.assertFalse(player.get_subscriptions()
                         .is_subscribed_to_team(test_teams[1].get("team_id")))

        # check sent onto to the homescreen
        self.assertEqual(next_action,
                         ActionKey.HOME_KEY)

    def testCaptain(self):
        """Test welcoming a Captain player"""
        message = Message(TestWelcome.TEST_SENDER_ID, message="")

        # the player is a captain this year
        test_teams = [self.random_team(captain=self.player.get_player_info()),
                      self.random_team(year=get_this_year() - 1)]
        self.platform.lookup_teams_player_associated_with\
            .return_value = test_teams

        # process the message
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)

        # check if the expected messages were sent back
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[1].get_message(),
                         Registration.ON_TEAM.value.format(test_teams[0]
                                                           .get("team_name")))
        self.assertEqual(messages[1].get_sender_id(),
                         TestWelcome.TEST_SENDER_ID)
        self.assertEqual(messages[2].get_message(),
                         Registration.WELCOME_CAPTAIN.value)
        self.assertEqual(messages[2].get_sender_id(),
                         TestWelcome.TEST_SENDER_ID)

        # make sure player was subscribed to team and is captain
        self.assertEqual(player.get_team_ids(),
                         [test_teams[0].get("team_id")])
        self.assertTrue(player.get_subscriptions()
                        .is_subscribed_to_team(test_teams[0].get("team_id")))
        self.assertTrue(player
                        .is_captain(team_id=test_teams[0].get("team_id")))

        # but not subscribed to team from last year
        self.assertFalse(player.get_subscriptions()
                         .is_subscribed_to_team(test_teams[1].get("team_id")))

        # check action state was updated
        self.assertEqual(next_action,
                         ActionKey.HOME_KEY)

    def testConvenor(self):
        """Test welcoming a convenor"""

        # set the person as a convenor and one some team
        self.db.set_convenors(
            [self.random_string(),
             self.player.get_player_info().get("player_name"),
             self.random_string()])
        test_teams = [self.random_team(),
                      self.random_team(year=get_this_year() - 1)]
        self.platform.lookup_all_teams.return_value = {
            test_teams[0].get("team_id"): test_teams[0],
            test_teams[1].get("team_id"): test_teams[1],
        }

        # process the message
        message = Message(TestWelcome.TEST_SENDER_ID, message="")
        (player, messages, next_action) = self.action.process(self.player,
                                                              message)

        # check if the expected messages were sent back
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].get_message(),
                         Registration.WELCOME_CONVENOR.value)
        self.assertEqual(messages[1].get_sender_id(),
                         TestWelcome.TEST_SENDER_ID)

        # make sure convenor is subscribed to all teams
        self.assertEqual(player.get_team_ids(),
                         [test_teams[0].get("team_id"),
                          test_teams[1].get("team_id")])
        self.assertTrue(player.get_subscriptions()
                        .is_subscribed_to_team(test_teams[0].get("team_id")))
        self.assertTrue(player.get_subscriptions()
                        .is_subscribed_to_team(test_teams[1].get("team_id")))

        # check action state was updated
        self.assertEqual(next_action, ActionKey.HOME_KEY)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
