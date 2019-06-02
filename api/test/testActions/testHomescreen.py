'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Welcome Action
'''
from api.actions.homescreen import Homescreen
from api.helper import get_this_year
from api.test.testDoubles.noAction import Nop
from api.message import Message
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.settings.action_keys import HOME_KEY, SUBMIT_SCORE_KEY
from api.settings.message_strings import MAIN_MENU_EVENTS_TITLE,\
    MAIN_MENU_FUN_TITLE, MAIN_MENU_LEAGUE_LEADERS_TITLE, FUN_TOTAL_COMMENT,\
    MAIN_MENU_UPCOMING_GAMES_TITLE, NO_UPCOMING_GAMES_COMMENT,\
    MAIN_MENU_SUBMIT_SCORE_TITLE, NOT_CAPTAIN_COMMENT
import unittest


class TestHomescreen(TestActionBase):

    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Homescreen Test Player Name"
    TEST_TEAM_ID = 1
    TEST_TEAM_NAME = "Homescreen Test Team Name"
    TEST_SENDER_ID = "homescreen_test_sender_id"

    def setUp(self):
        self.action_map = {HOME_KEY: Nop,
                           SUBMIT_SCORE_KEY: Nop}
        super(TestHomescreen, self).setUp()
        self.action = self.create_action(Homescreen)

    def background_setup(self, captain=False, convenor=False):
        """
            Setups some background such as the player and his teams

            Returns:
                test_teams: an array of teams he is part of
        """
        test_teams = [{"year": get_this_year() - 1,
                       "team_name": TestHomescreen.TEST_TEAM_NAME + "2",
                       "team_id": TestHomescreen.TEST_TEAM_ID + 1,
                       "captain": {"player_id":
                                   TestHomescreen.TEST_PLAYER_ID}}]
        player = Player(messenger_id=TestHomescreen.TEST_SENDER_ID,
                        name=TestHomescreen.TEST_PLAYER_NAME)
        if captain:
            player.make_captain({"team_id": TestHomescreen.TEST_TEAM_ID})
        if convenor:
            player.make_convenor()

        player.set_player_info({"player_id": TestHomescreen.TEST_PLAYER_ID})
        self.db.set_player(player)
        self.platform.set_mock_teams(teams=test_teams)
        return test_teams

    def testEvents(self):
        """
            Test getting the league events
        """
        # setup the background
        self.background_setup()
        mock_event = "Beerlympics"
        self.platform.set_mock_events({mock_event: "June 7th"})

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_EVENTS_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(mock_event in messages[0].get_message())

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testFunMeter(self):
        """
            Test getting fun meter
        """
        # setup the background
        self.background_setup()
        fun_count = 1
        mock_fun_meter = [{"year": get_this_year(), "count": fun_count}]
        self.platform.set_mock_fun_meter(mock_fun_meter)

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_FUN_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(FUN_TOTAL_COMMENT.format(fun_count) in
                        messages[0].get_message())

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testLeagueLeaders(self):
        """
            Test getting the league leaders
        """
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

        # process the action

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_LEAGUE_LEADERS_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
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

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testUpcomingGames(self):
        """
            Test getting the players upcoming games
        """
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

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_UPCOMING_GAMES_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
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

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testUpcomingGamesNoGames(self):
        """
            Test getting the players upcoming games
        """
        # setup the background
        self.background_setup()
        mock_upcoming_games = []
        self.platform.set_mock_upcoming_games(mock_upcoming_games)

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_UPCOMING_GAMES_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertTrue(NO_UPCOMING_GAMES_COMMENT in
                        messages[0].get_message())

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testDisplayOptions(self):
        """
            Test display the button options (player)
        """
        # setup the background
        self.background_setup()
        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 4)

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testDisplayOptionsCaptain(self):
        """
            Test display the button options (captain)
        """
        # setup the background
        self.background_setup(captain=True)
        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 5)

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testDisplayOptionsConvenor(self):
        """
            Test display the button options (Convenor)
        """
        # setup the background
        self.background_setup(convenor=True)
        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].get_message() is not None)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)
        self.assertEqual(len(messages[0].get_payload().get_options()), 5)

        # make sure the current action did not change
        self.assertTrue(self.db.inspect_saved_player() is None)

    def testSubmitGames(self):
        # setup the background
        self.background_setup(captain=True)

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_SUBMIT_SCORE_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 0)

        # make sure the current action did not change
        player = self.db.inspect_saved_player()
        self.assertTrue(player.get_action_state() is not None)
        self.assertEqual(player.get_action_state().get_id(), SUBMIT_SCORE_KEY)

    def testSubmitGamesNotCaptain(self):
        # setup the background
        self.background_setup()

        # process the action
        message = Message(TestHomescreen.TEST_SENDER_ID,
                          message=MAIN_MENU_SUBMIT_SCORE_TITLE)
        self.action.process(message, self.action_map)

        # check if expected message was sent back
        messages = self.messenger.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].get_message(), NOT_CAPTAIN_COMMENT)
        self.assertTrue(messages[0].get_sender_id,
                        TestHomescreen.TEST_SENDER_ID)

        # make sure the current action did not change
        player = self.db.inspect_saved_player()
        self.assertTrue(player is None)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
