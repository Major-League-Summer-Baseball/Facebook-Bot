'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test player class
'''
from api.players.subscription import Subscriptions
from api.players.player import Player
from api.actions import ActionState
from api.settings.action_keys import IDENTIFY_KEY
import unittest


class TestPlayer(unittest.TestCase):

    def testEmptyConstructor(self):
        """Test the empty constructor"""
        player = Player()
        self.assertFalse(player.is_convenor())
        self.assertFalse(player.is_captain(1))

        # test able to produce dictionary
        player.to_dictionary()

    def testConverion(self):
        """Test able to convert a player"""
        # the test player and its date
        test_name = "test name"
        test_id = "test id"
        test_player_info = {}
        test_teams = [1]
        test_captain = [1]
        test_subscription = Subscriptions()
        test_subscription.subscribe_to_team(1)
        test_action_state = ActionState(key=IDENTIFY_KEY)
        test = {"messenger_name": test_name,
                "messenger_id": test_id,
                "player_info": test_player_info,
                "teams": test_teams,
                "captain": test_captain,
                "subscriptions": test_subscription,
                "action_state": test_action_state
                }

        # create the player from a dictionary
        player = Player(dictionary=test)
        player_dict = player.to_dictionary()
        self.assertEqual(test["messenger_name"],
                         player_dict["messenger_name"])
        self.assertEqual(test["messenger_id"],
                         player_dict["messenger_id"])
        self.assertEqual(test["teams"],
                         player_dict["teams"])
        self.assertEqual(test["player_info"],
                         player_dict["player_info"])
        self.assertEqual(test["teams"],
                         player_dict["teams"])
        self.assertEqual(test["captain"],
                         player_dict["captain"])
        self.assertEqual(test["subscriptions"].to_dictionary(),
                         player_dict["subscriptions"])
        self.assertEqual(test["action_state"].to_dictionary(),
                         player_dict["action_state"])

        # make sure from_dictionary does not overwrite values
        player.from_dictionary({})
        player_dict = player.to_dictionary()
        print(player_dict)
        self.assertEqual(test["messenger_name"],
                         player_dict["messenger_name"])
        self.assertEqual(test["messenger_id"],
                         player_dict["messenger_id"])
        self.assertEqual(test["teams"],
                         player_dict["teams"])
        self.assertEqual(test["player_info"],
                         player_dict["player_info"])
        self.assertEqual(test["teams"],
                         player_dict["teams"])
        self.assertEqual(test["captain"],
                         player_dict["captain"])
        self.assertEqual(test["subscriptions"].to_dictionary(),
                         player_dict["subscriptions"])
        self.assertEqual(test["action_state"].to_dictionary(),
                         player_dict["action_state"])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
