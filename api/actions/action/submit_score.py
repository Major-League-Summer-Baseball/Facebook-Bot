'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Action for when a captain/convenor submits a score
'''
from typing import Tuple, List
from api.players.player import Player
from api.helper import convert_to_int, is_game_in_list_of_games
from api.actions import ActionKey, ActionState
from api.actions.action import Action
from api.message import Message, Option, Payload, GameFormatter
from api.settings.message_strings import ScoreSubmission
from api.errors import PlatformException


class SubmitScore(Action):
    """Submit the score"""
    DETERMINE_WHICH_GAME_STATE = "determine what game they want to submit"
    DETERMINE_WHICH_TEAM_STATE = "determine what team they want to submit for"
    ASK_METHOD_STATE = "what method would they like to use"
    LIST_OF_STATES = [DETERMINE_WHICH_GAME_STATE,
                      DETERMINE_WHICH_TEAM_STATE,
                      ASK_METHOD_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[ActionState, List[Message],
                                           ActionKey]:
        """Determine which method to use (by text or by buttons)"""

        # if not captain or convenor send them back to home page
        if not player.is_convenor() and not player.is_captain():
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.NOT_CAPTAIN.value)
            return (player, [message], ActionKey.HOME_KEY)

        current_state = player.get_action_state().get_state()
        if (current_state is None):

            if player.is_convenor() or len(player.get_teams_captain()) > 1:
                # determine what team they want to submit a game for
                return self.display_teams(player, message)
            else:

                # need to find what game they want to submit for
                team_id = str(player.get_teams_captain()[0])

                # store some team information that can
                # be used be submitting the score
                player = self.remember_team_for_player(player, team_id)
                return self.display_games(player, message)
        elif current_state == SubmitScore.DETERMINE_WHICH_TEAM_STATE:

            # received some team they picked
            return self.parse_team(player, message)
        elif current_state == SubmitScore.DETERMINE_WHICH_GAME_STATE:

            # received some game so need try to find it
            return self.parse_game(player, message)
        elif current_state == SubmitScore.ASK_METHOD_STATE:

            # determine which method they want to use
            return self.display_methods(player, message)
        elif current_state in SubmitScoreByText.LIST_OF_STATES:
            return SubmitScoreByText(self.database,
                                     self.platform).process(player, message)
        elif current_state in SubmitScoreByButtons.LIST_OF_STATES:
            return SubmitScoreByButtons(self.database,
                                        self.platform).process(player, message)

    def display_games(self, player: Player,
                      message: Message) -> Tuple[ActionState, List[Message],
                                                 ActionKey]:
        """Display the games"""
        action_state = player.get_action_state()

        # find the team they are submitting for
        team_id = action_state.get_data().get("team_id", None)
        if team_id is None:
            return self.display_teams(player, message)

        # get the games (from state otherwise make the API request)
        if action_state.get_data().get("games"):
            games = action_state.get_data().get("games")
        else:
            # get the games and remember them for later
            captain_id = action_state.get_data().get("captain_id", None)
            games = self.platform.games_to_submit_scores_for(player,
                                                             captain_id)
            data = action_state.get_data()
            data["games"] = games
            player.set_action_state(action_state.set_data(data))

        game_options = []
        for game in games:
            option = Option(GameFormatter(game).format(),
                            str(game.get("game_id")))
            game_options.append(option)

        # return to home screen since no games to submit for
        if len(game_options) == 0:
            return (player,
                    [Message(message.get_sender_id(),
                             recipient_id=message.get_recipient_id(),
                             message=ScoreSubmission.NO_GAMES.value)],
                    ActionKey.HOME_KEY)

        # add a cancel option
        game_options.append(Option(ScoreSubmission.CANCEL.value,
                                   ScoreSubmission.CANCEL.value))

        # update player state
        player.set_action_state(
            action_state.set_state(SubmitScore.DETERMINE_WHICH_GAME_STATE))

        # send them a list of games they can select
        payload = Payload(options=game_options)
        return (player,
                [Message(message.get_sender_id(),
                         recipient_id=message.get_recipient_id(),
                         message=ScoreSubmission.SELECT_GAME.value,
                         payload=payload)],
                None)

    def display_methods(self):
        pass

    def display_teams(self, player: Player,
                      message: Message) -> Tuple[Player, List[Message]]:
        """Displays the list of teams they can select to pick from"""

        # get the teams the player can submit scores for
        team_options = []
        team_lookup = {}
        if player.is_convenor():
            teams = self.platform.lookup_all_teams()
            for team_id, team in teams.items():
                team_name = get_team_name(team)
                team_lookup[str(team_id)] = team_name
                team_options.append(Option(team_name, str(team_id)))
        else:
            teams = self.platform.lookup_teams_player_associated_with(player)
            for team in teams:
                # if they are deemed a captain then list it as an option
                # this allows them to serve as a captain
                if player.is_captain(team_id=team.get("team_id")):
                    team_name = get_team_name(team)
                    team_options.append(Option(team_name,
                                               str(team.get("team_id"))))
                    team_lookup[str(team.get("team_id"))] = team_name

        if (len(team_options) == 0):
            # no teams to display
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.NOT_CAPTAIN.value)
            return (player, [message], ActionKey.HOME_KEY)

        for option in team_options:
            print(option.get_title())
        # sort the teams alphbetically
        team_options.sort(key=lambda option: option.get_title())

        # remember for later in case they write out the team name
        state = player.get_action_state()
        data = state.get_data()
        data["teams_lookup"] = team_lookup
        state.set_data(data)

        # update player state
        state.set_state(SubmitScore.DETERMINE_WHICH_TEAM_STATE)

        # remember the state
        player.set_action_state(state)

        # send them a list of teams they can select
        payload = Payload(options=team_options)
        message = Message(message.get_sender_id(),
                          recipient_id=message.get_recipient_id(),
                          message=ScoreSubmission.SELECT_TEAM.value,
                          payload=payload)
        return (player, [message], None)

    def parse_team(self, player: Player,
                   message: Message) -> Tuple[ActionState, List[Message],
                                              ActionKey]:
        """Parse the team response"""
        # check if they cancelled
        if self.did_they_cancel(message):
            return (player, [], ActionKey.HOME_KEY)

        # get the team id from the message payload or
        # parse it out of the message
        if message.get_payload() is not None:
            team_id = message.get_payload().get_options()[0].get_data()
        else:
            team_id = convert_to_int(message.get_message())
        action_state = player.get_action_state()
        team_keys = action_state.get_data().get("teams_lookup", {}).keys()

        if team_id is None or team_id not in team_keys:
            # TODO: try to figure out the team based upon the message
            # still need to figure out the team
            (player, messages, next_action) = self.display_teams(player,
                                                                 message)
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.UNRECOGNIZED_TEAM)
            return (player, [message] + messages, next_action)

        # lookup the team captain and see it
        player = self.remember_team_for_player(player, team_id)

        return self.display_games(player, message)

    def parse_game(self, player: Player,
                   message: Message) -> Tuple[ActionState, List[Message],
                                              ActionKey]:
        """Parses the game response"""
        # check if they cancelled
        if self.did_they_cancel(message):
            return (player, [], ActionKey.HOME_KEY)

        # get the game id from the message payload or
        # parse it out of the message
        if message.get_payload() is not None:
            game_id = message.get_payload().get_options()[0].get_data()
        else:
            game_id = convert_to_int(message.get_message())

        # TODO: try to figure out the game based upon the message
        # still need to figure out the game
        if (game_id is None or
                not is_game_in_list_of_games(
                    game_id,
                    player.get_action_state().get_data().get("games"))):

            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.UNRECOGNIZED_GAME.value)
            (player, messages, next_action) = self.display_games(player,
                                                                 message)
            return (player, [message] + messages, next_action)

        # remember the game id for later
        action_state = player.get_action_state()
        action_state.set_state(SubmitScoreByButtons.INITIAL_STATE)
        data = action_state.get_data()
        data["game_id"] = game_id
        player.set_action_state(action_state.set_data(data))

        # for now assuming what method they want to use
        # TODO: support multiple
        return SubmitScoreByButtons(self.database,
                                    self.platform).process(player, message)

    def remember_team_for_player(self, player: Player, team_id: str) -> Player:
        """Have the given player remember the team and its roster

        Args:
            player (Player): the player who is to remember the team
            team_id ([type]): the id of the team to remember

        Returns:
            Player: the player who remembers the team
        """
        state = player.get_action_state()
        data = state.get_data()
        data["teams_lookup"] = {str(team_id): "only one team"}
        data["team_id"] = team_id
        data["teamroster"] = self.platform.lookup_team_roster(team_id)
        data["captain_id"] = self.who_is_captain(data["teamroster"]
                                                 .get(team_id))
        player.set_action_state(state.set_data(data))
        return player

    def who_is_captain(self, team_roster: dict) -> int:
        """Who is the captain of the given team roster

        Args:
            team_roster (dict): a team roster object

        Raises:
            PlatformException: raised if no captain in the the list of players

        Returns:
            int: player id of the team captain
        """
        if team_roster.get("captain", None) is None:
            raise PlatformException(f"Given team has no captain {team_roster}")
        return team_roster.get("captain").get("player_id")

    def did_they_cancel(self, message: Message) -> bool:
        """Did the user mean to cancel based upon their message.

        Args:
             message [Message]: the message received

        Returns:
           bool: True if they meant to cancel otherwise False
        """
        if message.get_payload() is not None:
            if (ScoreSubmission.CANCEL.value.lower() in
                    message.get_payload().get_options()[0].get_data().lower()):
                return True
        else:
            if (ScoreSubmission.CANCEL.value.lower() in
                    message.get_message().lower()):
                return True
        return False


class SubmitScoreByText(Action):
    INITIAL_STATE = "starting to submit score by button"
    LIST_OF_STATES = [INITIAL_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[ActionState, List[Message],
                                           ActionKey]:
        return (player, [], None)


class SubmitScoreByButtons(Action):
    INITIAL_STATE = "starting to submit score by button"
    LIST_OF_STATES = [INITIAL_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[ActionState, List[Message],
                                           ActionKey]:
        return (player, [], None)


def get_team_name(team: dict) -> str:
    """Returns the team name of the given team"""
    return team.get("team_name", team.get("color", "name unknown"))
