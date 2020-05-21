'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Submit Score Action
'''
from typing import List, Tuple
from api.actions.action.submit_score import SubmitScore, SubmitScoreByButtons,\
                                            SubmitScoreByText
from api.message import Message, Option, Payload
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions import ActionKey
from api.helper import get_this_year
from api.settings.message_strings import ScoreSubmission, MainMenu
import unittest


class TestSubmitScore(TestActionBase):
    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Submit score test player name"
    TEST_TEAM_ID = 1
    TEST_TEAM_NAME = "Test team"
    TEST_SENDER_ID = "submit_score_test_sender_id"

    def setUp(self):
        super(TestSubmitScore, self).setUp()
        self.action = self.create_action(SubmitScore)
        self.player = Player(messenger_id=TestSubmitScore.TEST_SENDER_ID,
                             name=TestSubmitScore.TEST_PLAYER_NAME)
        player_info = {"player_id": TestSubmitScore.TEST_PLAYER_ID}
        self.player.set_player_info(player_info)

    def mockTeams(self, players: List[Player] = [],
                  number_of_teams: int = 1) -> Tuple[dict, dict]:
        """Mock a number of given teams with the given list of players.

        Args:
            players (List[Player], optional): players making roster.
                                              Defaults to [].
            number_of_teams (int, optional): the number of teams to mock.
                                             Defaults to 1.

        Returns:
            Tuple[dict, dict]: a list of teams and their team rosters
        """
        test_teams = []
        team_rosters = {}
        if len(players) > 0:
            captain = players[0].get_player_info()
        else:
            captain = self.random_player()
        for i in range(0, number_of_teams):
            test_team = {"year": get_this_year(),
                         "team_name": TestSubmitScore.TEST_TEAM_NAME + str(i),
                         "team_id": TestSubmitScore.TEST_TEAM_ID + i,
                         "players": players,
                         "captain": captain,
                         }
            test_teams.append(test_team)
            team_rosters[str(TestSubmitScore.TEST_TEAM_ID + i)] = test_team
        return (test_teams, team_rosters)

    def makePlayerCaptainOfTeams(self, player: Player,
                                 number_of_teams: int = 1) -> List[dict]:
        """Make the given player a captain of newly created team.

        Args:
            player (Player): the player to make captain
            number_of_teams (int): the number of teams to make
        Returns:
            List[dict]: a list containing the new teams
        """
        (test_teams,
         team_rosters) = self.mockTeams(players=[player],
                                        number_of_teams=number_of_teams)
        for team in test_teams:
            player.make_captain({"team_id": team.get("team_id")})
        self.db.set_player(self.player)
        self.platform.set_mock_teams(teams=test_teams)
        self.platform.set_mock_team_roster(team_rosters)
        return test_teams

    def testPosingAsCaptain(self):
        """Test someone posing as a captain/convenor"""
        all_states = (SubmitScore.LIST_OF_STATES +
                      SubmitScoreByText.LIST_OF_STATES +
                      SubmitScoreByButtons.LIST_OF_STATES)
        for state in all_states:
            # should not matter regardless of state
            self.player.set_action_state(
                self.player.get_action_state().set_state(state))
            message = Message(TestSubmitScore.TEST_SENDER_ID,
                              message=MainMenu.SUBMIT_SCORE_TITLE.value)
            (_, messages, next_action) = self.action.process(self.player,
                                                             message)
            self.assertEquals(len(messages), 1)
            self.assertEquals(messages[0].get_message(),
                              ScoreSubmission.NOT_CAPTAIN.value)
            self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCaptainCancelProcess(self):
        """Test a captain cancelling submission."""
        # make the player a captain
        self.makePlayerCaptainOfTeams(self.player)
        test_states = [SubmitScore.DETERMINE_WHICH_GAME_STATE,
                       SubmitScore.DETERMINE_WHICH_TEAM_STATE]
        normal_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=ScoreSubmission.CANCEL.value)
        cancel_option = Payload(options=[Option(ScoreSubmission.CANCEL.value,
                                                ScoreSubmission.CANCEL.value)])
        button_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message="",
                                 payload=cancel_option)
        for state in test_states:
            # set the action state
            self.player.set_action_state(
                self.player.get_action_state().set_state(state))

            # user types out cancel
            (_, messages, next_action) = self.action.process(self.player,
                                                             normal_message)
            for message in messages:
                print(message)
            self.assertEquals(len(messages), 0)
            self.assertEquals(next_action, ActionKey.HOME_KEY)

            # user clicks on the button
            (_, messages, next_action) = self.action.process(self.player,
                                                             button_message)
            self.assertEquals(len(messages), 0)
            self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCaptainWithNoGamesToSubmitFor(self):
        """Test a captain trying to submit but has no game"""
        # captain is player of one team
        self.makePlayerCaptainOfTeams(self.player)

        # there are no games to submit for
        self.platform.set_mock_games_to_submit_scores_for([])

        # first message received - should be sent back to home screen
        message = Message(TestSubmitScore.TEST_SENDER_ID,
                          message="")
        (_, messages, next_action) = self.action.process(self.player, message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.NO_GAMES.value)
        self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCaptainWithOneTeam(self):
        """Test a captain with one team going throught whole process."""
        # captain is player of one team
        team = self.makePlayerCaptainOfTeams(self.player)[0]
        other_team = self.random_team()
        # there is one game to submit
        game = self.random_game(team, other_team)
        self.platform.set_mock_games_to_submit_scores_for([game])

        message = Message(TestSubmitScore.TEST_SENDER_ID,
                          message="")
        (_, messages, next_action) = self.action.process(self.player, message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_GAME.value)
        self.assertIsNone(next_action)

        # pick the game we want to submit for
        game_option = Payload(options=[Option(game.get("game_id"),
                                              str(game.get("game_id")))])
        game_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=game_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              game_message)
        self.assertIsNone(next_action)

        # player should now be onto submitting game score by what ever method
        expect_states = (SubmitScoreByText.LIST_OF_STATES +
                         SubmitScoreByButtons.LIST_OF_STATES)
        self.assertTrue(player.get_action_state().get_state() in expect_states)

    def testCaptainWithMultipleTeams(self):
        """Test a captain with multiple teams to submit for."""
        # captain is player of two team
        team = self.makePlayerCaptainOfTeams(self.player, number_of_teams=2)[0]
        other_team = self.random_team()

        # there is one game to submit
        game = self.random_game(team, other_team)
        self.platform.set_mock_games_to_submit_scores_for([game])

        # process the first message - expect message asking for team
        message = Message(TestSubmitScore.TEST_SENDER_ID,
                          message="")
        (_, messages, next_action) = self.action.process(self.player, message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_TEAM.value)
        self.assertIsNone(next_action)

        # pick the team we want to submit for
        team_option = Payload(options=[Option(team.get("team_id"),
                                              str(team.get("team_id")))])
        team_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=team_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              team_message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_GAME.value)
        self.assertIsNone(next_action)

        # pick the game we want to submit for
        game_option = Payload(options=[Option(game.get("game_id"),
                                              str(game.get("game_id")))])
        game_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=game_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              game_message)
        self.assertIsNone(next_action)

        # player should now be onto submitting game score by what ever method
        expect_states = (SubmitScoreByText.LIST_OF_STATES +
                         SubmitScoreByButtons.LIST_OF_STATES)
        self.assertTrue(player.get_action_state().get_state() in expect_states)

    def testConvenorSubmittingScore(self):
        """Test a convenor submitting for some team."""
        # player is a convenor
        self.player.make_convenor()
        (test_teams,
         team_rosters) = self.mockTeams(number_of_teams=4)
        team = test_teams[0]
        other_team = test_teams[1]
        # there is one game to submit
        game = self.random_game(team, other_team)
        self.platform.set_mock_team_roster(team_rosters)
        self.platform.set_mock_teams(teams=test_teams)
        self.platform.set_mock_games_to_submit_scores_for([game])

        # process the first message - expect message asking for team
        message = Message(TestSubmitScore.TEST_SENDER_ID,
                          message="")
        (_, messages, next_action) = self.action.process(self.player, message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_TEAM.value)
        self.assertIsNone(next_action)

        # pick the team we want to submit for
        team_option = Payload(options=[Option(team.get("team_id"),
                                              str(team.get("team_id")))])
        team_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=team_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              team_message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_GAME.value)
        self.assertIsNone(next_action)

        # pick the game we want to submit for
        game_option = Payload(options=[Option(game.get("game_id"),
                                              str(game.get("game_id")))])
        game_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=game_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              game_message)
        self.assertIsNone(next_action)

        # player should now be onto submitting game score by what ever method
        expect_states = (SubmitScoreByText.LIST_OF_STATES +
                         SubmitScoreByButtons.LIST_OF_STATES)
        self.assertTrue(player.get_action_state().get_state() in expect_states)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
