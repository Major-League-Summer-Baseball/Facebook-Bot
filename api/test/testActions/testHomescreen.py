'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Welcome Action
'''
from api.helper import get_this_year
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions import ActionKey
from api.actions.action.homescreen import Homescreen
from api.settings.message_strings import HomescreenComments, MainMenu
import unittest


class TestHomescreen(TestActionBase):

    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Homescreen Test Player Name"
    TEST_TEAM_ID = 1
    TEST_TEAM_NAME = "Homescreen Test Team Name"
    TEST_SENDER_ID = "homescreen_test_sender_id"

    def setUp(self):
        super(TestHomescreen, self).setUp()
        self.action = self.create_action(Homescreen)
        self.player = Player(messenger_id=TestHomescreen.TEST_SENDER_ID,
                             name=TestHomescreen.TEST_PLAYER_NAME)
        player_info = {"player_id": TestHomescreen.TEST_PLAYER_ID}
        self.player.set_player_info(player_info)

    def background_setup(self, captain=False, convenor=False) -> dict:
        """The background setup for the homescreen.

        Args:
            captain (bool, optional): Make the player the captain.
                                      Defaults to False.
            convenor (bool, optional): Make the player a convenor.
                                       Defaults to False.

        Returns:
            List[dict]: the test teams created
        """
        test_teams = [{"year": get_this_year() - 1,
                       "team_name": TestHomescreen.TEST_TEAM_NAME + "2",
                       "team_id": TestHomescreen.TEST_TEAM_ID + 1,
                       "captain": {"player_id":
                                   TestHomescreen.TEST_PLAYER_ID}}]
        if captain:
            self.player.make_captain({"team_id": TestHomescreen.TEST_TEAM_ID})
        if convenor:
            self.player.make_convenor()
        self.db.set_player(self.player)
        self.platform.set_mock_teams(teams=test_teams)
        return test_teams

    def testEvents(self):
        """Test getting the league events."""
        # setup the background
        self.background_setup()
        mock_event = "Beerlympics"
        self.platform.set_mock_events({mock_event: "June 7th"})

        # process message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.EVENTS_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(mock_event in messages[0].get_message())

        # expecting no next action
        self.assertTrue(next_action is None)

    def testFunMeter(self):
        """Test getting fun meter."""
        # setup the background
        self.background_setup()
        fun_count = 1
        mock_fun_meter = [{"year": get_this_year(), "count": fun_count}]
        self.platform.set_mock_fun_meter(mock_fun_meter)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.FUN_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(HomescreenComments.FUN_TOTAL.value.format(fun_count) in
                        messages[0].get_message())

        # expecting no next action
        self.assertTrue(next_action is None)

    def testLeagueLeaders(self):
        """Test getting the league leaders."""
        # setup the background
        self.background_setup()
        mock_leaders = [{"name": "FemaleMalePlayer4",
                         "id": 24,
                         "hits": 12,
                         "team_id": 7,
                         "team": "Fireball Red",
                         "year": 2019
                         },
                        {"name": "Captain4",
                         "id": 11,
                         "hits": 9,
                         "team_id": 3,
                         "team": "Heaven Red",
                         "year": 2019
                         }]
        self.platform.set_mock_league_leaders(mock_leaders)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.LEAGUE_LEADERS_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 2)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(mock_leaders[0]["name"] in
                        messages[0].get_message())
        self.assertTrue(mock_leaders[1]["name"] in
                        messages[0].get_message())
        self.assertTrue(mock_leaders[0]["name"] in
                        messages[1].get_message())
        self.assertTrue(mock_leaders[1]["name"] in
                        messages[1].get_message())

        # expecting no next action
        self.assertTrue(next_action is None)

    def testUpcomingGames(self):
        """Test getting the players upcoming games."""
        # setup the background
        self.background_setup()
        mock_upcoming_games = [{"game_id": 19,
                                "home_team_id": 1,
                                "home_team": "Veritas Black",
                                "away_team_id": 2,
                                "away_team": "Ctrl V Blue",
                                "league_id": 1,
                                "date": "2019-05-31",
                                "time": "10:00",
                                "status": "To Be Played",
                                "field": "WP1"
                                },
                               {"game_id": 21,
                                "home_team_id": 1,
                                "home_team": "Veritas Black",
                                "away_team_id": 3,
                                "away_team": "Heaven Red",
                                "league_id": 1,
                                "date": "2019-05-31",
                                "time": "11:00",
                                "status": "To Be Played",
                                "field": "WP1"
                                }]
        self.platform.set_mock_upcoming_games(mock_upcoming_games)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.UPCOMING_GAMES_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(mock_upcoming_games[0]["home_team"] in
                        messages[0].get_message())
        self.assertTrue(mock_upcoming_games[0]["away_team"] in
                        messages[0].get_message())
        self.assertTrue(mock_upcoming_games[0]["field"] in
                        messages[0].get_message())
        self.assertTrue(mock_upcoming_games[1]["home_team"] in
                        messages[0].get_message())
        self.assertTrue(mock_upcoming_games[1]["away_team"] in
                        messages[0].get_message())
        self.assertTrue(mock_upcoming_games[1]["field"] in
                        messages[0].get_message())

        # expecting no next action
        self.assertTrue(next_action is None)

    def testUpcomingGamesNoGames(self):
        """Test getting the players upcoming games."""
        # setup the background
        self.background_setup()
        mock_upcoming_games = []
        self.platform.set_mock_upcoming_games(mock_upcoming_games)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.UPCOMING_GAMES_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(HomescreenComments.NO_UPCOMING_GAMES.value in
                        messages[0].get_message())

        # expecting no next action
        self.assertTrue(next_action is None)

    def testDisplayOptions(self):
        """Test display the button options (player)."""
        # setup the background
        self.background_setup()

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 4)

        # expecting no next action
        self.assertTrue(next_action is None)

    def testDisplayOptionsCaptain(self):
        """Test display the button options (captain)"""
        # setup the background
        self.background_setup(captain=True)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 5)

        # expecting no next action
        self.assertTrue(next_action is None)

    def testDisplayOptionsConvenor(self):
        """Test display the button options (Convenor)."""
        # setup the background
        self.background_setup(convenor=True)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 5)

        # expecting no next action
        self.assertTrue(next_action is None)

    def testSubmitGames(self):
        # setup the background
        self.background_setup(captain=True)

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.SUBMIT_SCORE_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 0)

        # make sure the next action is to submit
        self.assertEqual(next_action,
                         ActionKey.SUBMIT_SCORE_KEY)

    def testSubmitGamesNotCaptain(self):
        # setup the background
        self.background_setup()

        # process the message
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MainMenu.SUBMIT_SCORE_TITLE.value)
        (_, messages, next_action) = self.action.process(self.player, message)

        # check if expected message was sent back
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].get_message(),
                         HomescreenComments.NOT_CAPTAIN.value)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)

        # expecting no next action
        self.assertTrue(next_action is None)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
