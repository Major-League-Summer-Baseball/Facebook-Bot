'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Test Submit Score Action
'''
from typing import List, Tuple
from api.mlsb.typing import GameSheet, Game, PlayerInfo, Team, TeamRoster
from api.actions.action.submit_score import SubmitScore, SubmitScoreByButtons,\
                                            SubmitScoreByText

from api.message import Message, Option, Payload
from api.players.player import Player
from api.test.testActions import TestActionBase
from api.actions import ActionKey
from api.helper import get_this_year
from api.settings.message_strings import ScoreSubmission, MainMenu
import unittest


TEAM_ROSTER = "teamroster"
TEAM_LOOKUP = "team_lookup"
GAMES = "games"
GAME_SHEET = "game_sheet"
BATTER_ID = "batter_id"
INITIAL_STATE = SubmitScoreByButtons.INITIAL_STATE


def setSubmitScoreBackground(player: Player, teamroster: List[Player],
                             game: dict,
                             state: str = INITIAL_STATE) -> Player:
    """Set the background of the given player

    Args:
        player (Player): the player submitting the score
        teamroster (List[Player]): a list of players on the roster
        game (dict): the game the player is submitting for
        state (str): the action state to set player as

    Returns:
        Player: the player with their background set
    """
    action_state = player.get_action_state()
    data = action_state.get_data()
    data[GAMES] = [game]
    data[Game.ID] = game.get(Game.ID)
    data[TEAM_ROSTER] = teamroster
    data[Team.CAPTAIN] = player.get_player_info()
    action_state.set_data(data)
    action_state.set_state(state)
    player.set_action_state(action_state)
    return player


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
        player_info = {PlayerInfo.ID: TestSubmitScore.TEST_PLAYER_ID}
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
            test_team = {Team.YEAR: get_this_year(),
                         Team.NAME: TestSubmitScore.TEST_TEAM_NAME + str(i),
                         Team.ID: TestSubmitScore.TEST_TEAM_ID + i,
                         TeamRoster.PLAYERS: players,
                         Team.CAPTAIN: captain,
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
            player.make_captain({Team.ID: team.get(Team.ID)})
        self.platform.lookup_teams_player_associated_with\
            .return_value = test_teams
        self.db.set_player(self.player)
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
        self.platform.games_to_submit_scores_for.return_value = []

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
        self.platform.games_to_submit_scores_for.return_value = [game]

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

        # player should now be asked which method to use
        self.assertEquals(len(messages), 1)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScore.DETERMINE_WHICH_METHOD_STATE)
        self.assertIsNone(next_action)

        # now pick a method - using text
        text_option = Option(ScoreSubmission.TEXT_METHOD.value,
                             str(ScoreSubmission.TEXT_METHOD.value))
        method_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message="",
                                 payload=Payload(options=[text_option]))
        (player, messages, next_action) = self.action.process(self.player,
                                                              method_message)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScoreByText.INITIAL_STATE)
        self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCaptainWithMultipleTeams(self):
        """Test a captain with multiple teams to submit for."""
        # captain is player of two team
        team = self.makePlayerCaptainOfTeams(self.player, number_of_teams=2)[0]
        other_team = self.random_team()

        # there is one game to submit
        game = self.random_game(team, other_team)
        self.platform.games_to_submit_scores_for.return_value = [game]

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

        # player should now be asked which method to use
        self.assertEquals(len(messages), 1)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScore.DETERMINE_WHICH_METHOD_STATE)
        self.assertIsNone(next_action)

        # now pick a method - using text
        text_option = Option(ScoreSubmission.TEXT_METHOD.value,
                             str(ScoreSubmission.TEXT_METHOD.value))
        method_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message="",
                                 payload=Payload(options=[text_option]))
        (player, messages, next_action) = self.action.process(self.player,
                                                              method_message)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScoreByText.INITIAL_STATE)
        self.assertEquals(next_action, ActionKey.HOME_KEY)

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
        self.platform.lookup_all_teams.return_value = {
            team.get(Team.ID): team for team in test_teams}
        self.platform.lookup_team_roster.return_value = team
        self.platform.games_to_submit_scores_for.return_value = [game]

        # process the first message - expect message asking for team
        message = Message(TestSubmitScore.TEST_SENDER_ID,
                          message="")
        (_, messages, next_action) = self.action.process(self.player, message)
        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SELECT_TEAM.value)
        self.assertIsNone(next_action)

        # pick the team we want to submit for
        team_option = Payload(options=[Option(team.get(Team.ID),
                                              str(team.get(Team.ID)))])
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
        game_option = Payload(options=[Option(game.get(Game.ID),
                                              str(game.get(Game.ID)))])
        game_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message="",
                               payload=game_option)
        (player, messages, next_action) = self.action.process(self.player,
                                                              game_message)

        # player should now be asked which method to use
        self.assertEquals(len(messages), 1)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScore.DETERMINE_WHICH_METHOD_STATE)
        self.assertIsNone(next_action)

        # now pick a method - using buttons
        text_option = Option(ScoreSubmission.BUTTON_METHOD.value,
                             str(ScoreSubmission.BUTTON_METHOD.value))
        method_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message="",
                                 payload=Payload(options=[text_option]))
        (player, messages, next_action) = self.action.process(self.player,
                                                              method_message)
        self.assertEquals(player.get_action_state().get_state(),
                          SubmitScoreByButtons.DETERMINE_SCORE_STATE)
        self.assertIsNone(next_action)


class TestSubmitScoreByButtons(TestActionBase):
    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Submit score test player name"
    TEST_TEAM_ID = 1
    TEST_TEAM_NAME = "Test team"
    TEST_SENDER_ID = "submit_score_test_sender_id"

    def setUp(self):
        super(TestSubmitScoreByButtons, self).setUp()
        # initialize tha ction
        self.action = self.create_action(SubmitScore)

        # setup the player who is the captain who is submitting the score
        self.player = Player(messenger_id=TestSubmitScore.TEST_SENDER_ID,
                             name=TestSubmitScore.TEST_PLAYER_NAME)
        player_info = self.random_player(gender="M")
        player_info[PlayerInfo.ID] = TestSubmitScore.TEST_PLAYER_ID
        self.player.set_player_info(player_info)

        # setup their background for the game they are submitting for
        self.my_team = self.random_team(captain=player_info)
        self.player.make_captain(self.my_team)
        self.other_team = self.random_team()
        self.game = self.random_game(self.my_team, self.other_team)
        self.roster = self.my_team
        self.roster["captain"] = player_info
        self.roster["players"] = [self.random_player(gender="F"),
                                  self.random_player(gender="M"),
                                  player_info]
        self.player = setSubmitScoreBackground(
            self.player,
            self.roster,
            self.game,
            SubmitScoreByButtons.INITIAL_STATE)

    def initial_message(self, player: Player,
                        use_payload: bool = False) -> Player:
        """ Send an inital message"""
        # send initial message
        if use_payload:
            text_option = Option(ScoreSubmission.BUTTON_METHOD.value,
                                 str(ScoreSubmission.BUTTON_METHOD.value))
            method_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     message="",
                                     payload=Payload(options=[text_option]))
        else:
            m = ScoreSubmission.BUTTON_METHOD.value
            method_message = Message(TestSubmitScore.TEST_SENDER_ID, message=m)
        (player, messages,
            next_action) = self.action.process(player, method_message)

        # get asked for score
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.ASK_FOR_SCORE.value)
        return player

    def send_score(self, player: Player, score: str,
                   use_payload: bool = False) -> Player:
        """Send the score"""
        # send message with score
        if use_payload:
            score_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                    message=None,
                                    payload=Payload(options=[Option(score,
                                                                    score)]))
        else:
            score_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                    message=f"we had {score} runs")
        (player, messages,
            next_action) = self.action.process(player, score_message)

        # now asked about HR
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)
        return player

    def pick_batter(self, player: Player, batter: dict, hits: str,
                    use_payload: bool = False) -> Player:
        """Pick a batter and specify their number of hits"""
        ss_state = SubmitScoreByButtons.DETERMINE_SS_BATTER_STATE
        category = (GameSheet.SS
                    if player.get_action_state().get_state() == ss_state
                    else GameSheet.HR)
        # pick the batter
        if use_payload:
            batter_option = Payload(options=[Option(batter.get("player_name"),
                                             str(batter.get("player_id")))])
            batter_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     payload=batter_option)
        else:
            batter_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     message=batter.get("player_name"))
        (player, messages,
            next_action) = self.action.process(player, batter_message)

        # now ask for how many
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        expected_message = ScoreSubmission.HOW_HITS_PLAYER.value.format(
            batter.get("player_name"))
        self.assertEquals(expected_message, messages[0].get_message())

        if use_payload:
            hit = Payload(options=[Option(hits, hits)])
            hit_message = Message(TestSubmitScore.TEST_SENDER_ID, payload=hit)
        else:
            hit_message = Message(TestSubmitScore.TEST_SENDER_ID, message=hits)
        (player, messages,
            next_action) = self.action.process(player, hit_message)

        # back to picking batter
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        expected_message = (ScoreSubmission.SS_SELECT_PLAYER.value
                            if category == GameSheet.SS
                            else ScoreSubmission.HR_SELECT_PLAYER.value)
        self.assertEquals(expected_message, messages[0].get_message())
        return player

    def get_to_submit_review(self, score: str,
                             hrs: List[Tuple[dict, str]],
                             ss: List[Tuple[dict, str]],
                             use_payload: bool = False) -> Player:
        """Send messages to get to the review screen"""
        player = self.initial_message(self.player, use_payload=use_payload)
        player = self.send_score(player, score, use_payload=use_payload)

        # submit the number of homeruns
        for (batter, hits) in hrs:
            player = self.pick_batter(player, batter, hits,
                                      use_payload=use_payload)

        # say done to submitting homeruns
        if use_payload:
            done_option = Option(ScoreSubmission.DONE.value,
                                 ScoreSubmission.DONE.value)
            done_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                   message=None,
                                   payload=Payload(options=[done_option]))
        else:
            done_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                   message=ScoreSubmission.DONE.value)
        (player, messages,
            next_action) = self.action.process(player, done_message)

        # now asked about SS
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

        # submit the number of ss
        for (batter, hits) in ss:
            player = self.pick_batter(player, batter, hits,
                                      use_payload=use_payload)

        # say done
        (player, messages,
            next_action) = self.action.process(player, done_message)

        # now given summary
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertTrue(f"score: {score}" in messages[0].get_message().lower())
        return player

    def testSendingScoreAsWord(self):
        """Test sending the score as a word"""
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

    def testHandleNoScore(self):
        """Test able to ask for again if cant find one"""
        player = self.initial_message(self.player)
        unknown_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                  message="sorry what?")
        (player, messages,
            next_action) = self.action.process(player, unknown_message)

        # asked again for the score
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.ASK_FOR_SCORE.value)

    def testUnknownBatter(self):
        """Test able to handle when given message with no batter information"""
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        unknown_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                  message="sorry what?")
        (player, messages,
            next_action) = self.action.process(player, unknown_message)

        # asked again for the score
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.UNRECOGNIZED_PLAYER.value)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)

    def testAmbiguousBatter(self):
        """Test able to handle when given message matches multiple players"""

        # setup a situation where match to players
        self.roster["players"][0]['player_name'] = "Player One"
        self.roster["players"][1]['player_name'] = "Player Two"
        self.player = setSubmitScoreBackground(
            self.player,
            self.roster,
            self.game,
            SubmitScoreByButtons.INITIAL_STATE)

        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        unknown_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                  message="Player")
        (player, messages,
            next_action) = self.action.process(player, unknown_message)

        # asked again for batter
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        expected_message = ScoreSubmission.AMBIGUOUS_PLAYER.value.format(
            "Player One and Player Two")
        self.assertEquals(messages[0].get_message(), expected_message)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)

    def testHrIneligiblePlayer(self):
        """Test where the player is ineligible for the homeruns"""

        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        # already select a batter
        batter = self.roster.get(TeamRoster.PLAYERS)[0]
        player = self.pick_batter(player, batter, "1")

        # not try them again
        player.get_action_state().get_data().get(GameSheet.HR)
        name = batter.get(PlayerInfo.NAME)
        ineligible_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     message=name)
        (player, messages,
            next_action) = self.action.process(player, ineligible_message)

        # asked again for batter
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.PLAYER_NOT_ELIGIBLE.value)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)

    def testSSIneligiblePlayer(self):
        """Test where the player is ineligible for the ss"""

        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        # done with homeruns
        done_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message=ScoreSubmission.DONE.value)
        (player, messages,
            next_action) = self.action.process(player, done_message)

        # now asked about SS
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

        # already select a batter
        batter = self.roster.get(TeamRoster.PLAYERS)[0]
        player = self.pick_batter(player, batter, "1")

        # not try them again
        player.get_action_state().get_data().get(GameSheet.HR)
        name = batter.get(PlayerInfo.NAME)
        ineligible_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     message=name)
        (player, messages,
            next_action) = self.action.process(player, ineligible_message)

        # asked again for batter
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.PLAYER_NOT_ELIGIBLE.value)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

    def testMaleNotEligibleForSS(self):
        """Test males are not elgible for SS category"""
        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        # done with homeruns
        done_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message=ScoreSubmission.DONE.value)
        (player, messages,
            next_action) = self.action.process(player, done_message)
        # now asked about SS
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

        # try submitting a male player
        name = self.roster.get(TeamRoster.PLAYERS)[1].get(PlayerInfo.NAME)
        ineligible_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                     message=name)
        (player, messages,
            next_action) = self.action.process(player, ineligible_message)

        # asked again for batter
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.PLAYER_NOT_ELIGIBLE.value)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

    def testHRLessThanRBI(self):
        """Test that homeruns must be less than runs"""
        # get to batter screen
        score = 3
        player = self.initial_message(self.player)
        self.send_score(player, score)

        name = self.roster.get(TeamRoster.PLAYERS)[0].get(PlayerInfo.NAME)
        batter_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=name)
        (player, messages,
            next_action) = self.action.process(player, batter_message)

        # now ask for how many
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        expected_message = ScoreSubmission.HOW_HITS_PLAYER.value.format(name)
        self.assertEquals(expected_message, messages[0].get_message())

        # say too many with homeruns
        too_many_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                   message=score + 3)
        (player, messages,
            next_action) = self.action.process(player, too_many_message)
        # now asked about HR
        self.assertIsNone(next_action)
        self.assertEquals(2, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.TOO_MANY_HRS.value)
        self.assertEquals(messages[1].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)

    def testCancelBatterHRSelection(self):
        """Test able to cancel picking number for batter"""
        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        # pick wrong batter
        batter = self.roster[TeamRoster.PLAYERS][0]
        wrong_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                message=batter.get(PlayerInfo.NAME))
        (player, messages,
            next_action) = self.action.process(player, wrong_message)
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.HOW_HITS_PLAYER.value.format(
                              batter.get(PlayerInfo.NAME)))

        # cancel selection
        cancel_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=ScoreSubmission.CANCEL.value)
        (player, messages,
            next_action) = self.action.process(player, cancel_message)
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.HR_SELECT_PLAYER.value)

        # cancel back to homepage
        (player, messages,
            next_action) = self.action.process(player, cancel_message)
        self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCancelBatterSSSelection(self):
        """Test able to cancel picking number for batter"""
        # get to batter screen
        player = self.initial_message(self.player)
        self.send_score(player, "eleven")

        # done with homeruns
        done_message = Message(TestSubmitScore.TEST_SENDER_ID,
                               message=ScoreSubmission.DONE.value)
        (player, messages,
            next_action) = self.action.process(player, done_message)
        # now asked about SS
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)
        # pick wrong batter
        batter = self.roster.get(TeamRoster.PLAYERS)[0]
        wrong_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                message=batter.get(PlayerInfo.NAME))
        (player, messages,
            next_action) = self.action.process(player, wrong_message)
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.HOW_HITS_PLAYER.value.format(
                              batter.get(PlayerInfo.NAME)))

        # cancel selection
        cancel_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=ScoreSubmission.CANCEL.value)
        (player, messages,
            next_action) = self.action.process(player, cancel_message)
        self.assertIsNone(next_action)
        self.assertEquals(1, len(messages))
        self.assertEquals(messages[0].get_message(),
                          ScoreSubmission.SS_SELECT_PLAYER.value)

        # cancel back to homepage
        (player, messages,
            next_action) = self.action.process(player, cancel_message)
        self.assertEquals(next_action, ActionKey.HOME_KEY)

    def testCancelSubmission(self):
        """Test cancelling on the review screens."""
        # submit everything up until game sheet review
        player = self.get_to_submit_review("11", [], [])

        # now say cancel
        cancel_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=ScoreSubmission.CANCEL.value)
        (player, messages,
            next_action) = self.action.process(player, cancel_message)

        # now should be back at homepage
        self.assertEquals(next_action, ActionKey.HOME_KEY)

        # ensure no game sheet was submitted at all
        self.assertFalse(self.platform.submit_game_sheet.called)

    def testCancelSubmissionByPayload(self):
        """Test cancelling on the review screen using a payload"""
        # submit everything up until game sheet review
        player = self.get_to_submit_review("11", [], [], use_payload=True)

        # now say cancel
        cancel_option = Option(ScoreSubmission.CANCEL.value,
                               ScoreSubmission.CANCEL.value)
        cancel_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 payload=Payload(options=[cancel_option]))
        (player, messages,
            next_action) = self.action.process(player, cancel_message)

        # now should be back at homepage
        self.assertEquals(next_action, ActionKey.HOME_KEY)

        # ensure no game sheet was submitted at all
        self.assertFalse(self.platform.submit_game_sheet.called)

    def testSubmissionUsingMessages(self):
        """Test a submission using just messages"""
        # submit everything up until game sheet review
        score = "11"
        female = self.roster.get(TeamRoster.PLAYERS)[0]
        male = self.roster.get(TeamRoster.PLAYERS)[1]
        player = self.get_to_submit_review(score, [(male, "1 hr")],
                                           [(female, "2 ss")])

        # now say submit
        submit_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=ScoreSubmission.SUBMIT.value)
        (player, messages,
            next_action) = self.action.process(player, submit_message)

        # now should be back at homepage
        self.assertEquals(next_action, ActionKey.HOME_KEY)

        # ensure the game sheet submitted makes sense
        expected_game_sheet = {
            GameSheet.HR: [male.get(PlayerInfo.ID)],
            GameSheet.SS: 2 * [female.get(PlayerInfo.ID)],
            GameSheet.SCORE: int(score),
            GameSheet.GAME_ID: self.game.get(Game.ID),
            GameSheet.PLAYER_ID: self.player.get_player_id()
        }
        self.assertTrue(self.platform.submit_game_sheet)
        self.platform.submit_game_sheet.assert_called_with(expected_game_sheet)

    def testSubmissionUsingPayloads(self):
        """Test a submission using just paylods"""
        # submit everything up until game sheet review
        score = "11"
        female = self.roster.get(TeamRoster.PLAYERS)[0]
        male = self.roster.get(TeamRoster.PLAYERS)[1]
        player = self.get_to_submit_review(score, [(male, "1")],
                                           [(female, "2")],
                                           use_payload=True)

        # now say submit
        submit_option = Option(ScoreSubmission.SUBMIT.value,
                               ScoreSubmission.SUBMIT.value)
        submit_message = Message(TestSubmitScore.TEST_SENDER_ID,
                                 message=None,
                                 payload=Payload(options=[submit_option]))
        (player, messages,
            next_action) = self.action.process(player, submit_message)

        # now should be back at homepage
        self.assertEquals(next_action, ActionKey.HOME_KEY)

        # ensure the game sheet submitted makes sense
        expected_game_sheet = {
            GameSheet.HR: [male.get(PlayerInfo.ID)],
            GameSheet.SS: 2 * [female.get(PlayerInfo.ID)],
            GameSheet.SCORE: int(score),
            GameSheet.GAME_ID: self.game.get(Game.ID),
            GameSheet.PLAYER_ID: self.player.get_player_id()
        }
        self.assertTrue(self.platform.submit_game_sheet)
        self.platform.submit_game_sheet.assert_called_with(expected_game_sheet)


class TestSubmitScoreByText(TestActionBase):
    TEST_PLAYER_ID = 1
    TEST_PLAYER_NAME = "Submit score test player name"
    TEST_TEAM_ID = 1
    TEST_TEAM_NAME = "Test team"
    TEST_SENDER_ID = "submit_score_test_sender_id"

    def setUp(self):
        super(TestSubmitScoreByText, self).setUp()
        self.action = self.create_action(SubmitScore)
        self.player = Player(messenger_id=TestSubmitScore.TEST_SENDER_ID,
                             name=TestSubmitScore.TEST_PLAYER_NAME)
        player_info = {PlayerInfo.ID: TestSubmitScore.TEST_PLAYER_ID}
        self.player.set_player_info(player_info)

    def setupBackground(self):
        self.team = self.random_team()

    def testSetup(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
