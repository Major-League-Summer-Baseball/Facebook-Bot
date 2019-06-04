'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Submit Score Action
'''
from api.actions.submit_score import SubmitScore
from api.helper import get_this_year
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.settings.action_keys import SUBMIT_SCORE_KEY, HOME_KEY
from api.test.testDoubles.noAction import Nop
from api.settings.message_strings import NOT_CAPTAIN_COMMENT


class TestSubmitScore(TestActionBase):
    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Submit Score Test Player Name"
    TEST_TEAM_ID_ONE = 1
    TEST_TEAM_NAME_ONE = "Test Team One"
    TEST_SENDER_ID = "submit_score_test_sender_id"

    def setUp(self):
        self.action_map = {HOME_KEY: Nop, SUBMIT_SCORE_KEY: Nop}
        super(TestSubmitScore, self).setUp()
        self.action = self.create_action(SubmitScore)

        MOCK_GAME_ONE = {"game_id": 1,
                         "home_team_id": 1,
                         "home_team": "Test Team 2",
                         "away_team_id": 2,
                         "away_team": "Amsterdam Brewery Blue",
                         "league_id": 1,
                         "date": "2019-06-03",
                         "time": "10:00",
                         "status": "To Be Played",
                         "field": "WP1"}

    def background_setup(self, captain=False, convenor=False):
        """
            Setups some backgorund such as the player and his teams
            Returns:
                test_teams: an arrays of teams the player is part of
        """
        player_info = self.random_player()
        team_one = self.random_team(captain_id=player_info.get("player_id"))
        test_teams = [team_one]

        player = Player(messenger_id=TestSubmitScore.TEST_SENDER_ID,
                        name=TestSubmitScore.TEST_PLAYER_NAME)
        if captain:
            player.make_captain({"team_id": TestSubmitScore.TEST_TEAM_ID})
        if convenor:
            player.make_convenor()

        player.set_player_info({"player_id": TestSubmitScore.TEST_PLAYER_ID})
        self.db.set_player(player)
        self.platform.set_mock_teams(teams=test_teams)
        return test_teams

    def testNotCaptainMessage(self):
        """
            Test getting a message from just a player (not convenor or captain)
        """
        self.background_setup()

        # process the action
        message = Message(TestSubmitScore.TEST_SENDER_ID, message="")
        self.action.process(message, self.action_map)

        # check got a not captain message
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestSubmitScore.TEST_SENDER_ID)
        self.assertTrue(NOT_CAPTAIN_COMMENT in messages[0].get_message())

        # make sure they got sent back to homescreen
        player = self.db.inspect_saved_player()
        self.assertTrue(player.get_action_state() is not None)
        self.assertEqual(player.get_action_state().get_id(), HOME_KEY)

    def testCaptainOneTeamFirstMessage(self):
        """
            Test getting a message from a normal captain (just one team)
        """
        self.background_setup(captain=True)

        # stub some of the platform responses
        mock_team_roster = {"player_id": TestSubmitScore.TEST_PLAYER_ID,
                            "player_name": TestSubmitScore.TEST_PLAYER_NAME}
        self.platform.set_mock_team_roster(mock_team_roster)
        mock_games = [{"game_id": 1}]
        # process the action
        message = Message(TestSubmitScore.TEST_SENDER_ID, message="")
        self.action.process(message, self.action_map)

        # check got a not captain message
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestSubmitScore.TEST_SENDER_ID)
        self.assertTrue(NOT_CAPTAIN_COMMENT in messages[0].get_message())

        # make sure they got sent back to homescreen
        player = self.db.inspect_saved_player()
        self.assertTrue(player.get_action_state() is not None)
        self.assertEqual(player.get_action_state().get_id(), SUBMIT_SCORE_KEY)

    def testConvenorFirstMessage(self):
        pass
