'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Action for when a captain/convenor submits a score
'''
from typing import Tuple, List
from api.platform import TeamRoster, Team, PlayerInfo, GameSheet, Game
from api.players.player import Player
from api.parsers import parse_number, match_with_player
from api.helper import is_game_in_list_of_games
from api.actions import ActionKey
from api.actions.action import Action
from api.message import Message, Option, Payload, GameFormatter
from api.settings.message_strings import ScoreSubmission, GameSheetOverview
from api.errors import PlatformException, GameDoesNotExist, NotCaptainException

# confidence with assuming correctness
CONFIDENCE_LEVEL = 0.60

# various contstant that are used as keys
TEAM_ROSTER = "teamroster"
TEAM_LOOKUP = "team_lookup"
GAMES = "games"
GAME_SHEET = "game_sheet"
BATTER_ID = "batter_id"


def get_team_name(team: Team) -> str:
    """Get the team name from the team.

    Args:
        team (Team): the team

    Returns:
        str: the team name if present otherwise its color
    """
    return team.get(Team.NAME, team.get(Team.COLOR, "name unknown"))


def did_they_cancel(message: Message) -> bool:
    """Did the user mean to cancel based upon their message.

    Args:
        message [Message]: the message received

    Returns:
        bool: True if they meant to cancel otherwise False
    """
    if message.get_payload() is not None:
        payload = message.get_payload().get_options()[0].get_data()
        if (ScoreSubmission.CANCEL.value.lower().strip() in
                payload.lower().strip()):
            return True
    else:
        if (ScoreSubmission.CANCEL.value.lower().strip() in
                str(message.get_message()).lower().strip()):
            return True
    return False


def are_they_done(message: Message) -> bool:
    """Are they done with the current step.

    Args:
        message (Message): the message received

    Returns:
        bool: True if done with current step
    """
    if message.get_payload() is not None:
        payload = message.get_payload().get_options()[0].get_data()
        if (ScoreSubmission.DONE.value.lower().strip() in
                payload.lower().strip()):
            return True
    else:
        if (ScoreSubmission.DONE.value.lower().strip() in
                str(message.get_message()).lower().strip()):
            return True
    return False


def did_they_submit(message: Message) -> bool:
    """Are they done with the current step.

    Args:
        message (Message): the message received

    Returns:
        bool: True if done with current step
    """
    if message.get_payload() is not None:
        payload = message.get_payload().get_options()[0].get_data()
        if (ScoreSubmission.SUBMIT.value.lower().strip() in
                payload.lower().strip()):
            return True
    else:
        if (ScoreSubmission.SUBMIT.value.lower().strip() in
                message.get_message().lower().strip()):
            return True
    return False


def who_is_captain(team_roster: TeamRoster) -> PlayerInfo:
    """Returns who is the captain of the given.

    Args:
        team_roster (TeamRoster): the team roser

    Raises:
        PlatformException: given a team with no captain

    Returns:
        PlayerInfo: the player who is the captain
    """
    if team_roster.get(TeamRoster.CAPTAIN, None) is None:
        raise PlatformException(f"Given team has no captain {team_roster}")
    return team_roster.get(TeamRoster.CAPTAIN)


def init_gamesheet(player: Player) -> Player:
    """Initialize the data structure for the score data.

    Args:
        player (Player): the player submitting the score

    Returns:
        Player: player with the update data
    """
    action_state = player.get_action_state()
    data = action_state.get_data()
    data[GAME_SHEET] = {
        GameSheet.GAME_ID: data.get(Game.ID),
        GameSheet.PLAYER_ID: data.get(TeamRoster.CAPTAIN).get(PlayerInfo.ID),
        GameSheet.SCORE: None,
        GameSheet.HR: [],
        GameSheet.SS: []
    }
    player.set_action_state(action_state.set_data(data))
    return player


def player_eligible_for_category(game_sheet: GameSheet, player: PlayerInfo,
                                 category: str) -> bool:
    """Returns whether the given player is elgible for the given category.

    Args:
        game_sheet (GameSheet): holds the game score object
        player (PlayerInfo): the player to check
        category (str): the category to check
    Returns:
        bool: True if player is eligible False
    """
    return (player.get(PlayerInfo.ID) not in game_sheet[category] and
            (category == GameSheet.HR or
             player.get(PlayerInfo.GENDER).lower() == PlayerInfo.FEMALE))


def is_score_valid(score: int) -> bool:
    """Is the score a valid score.

    Args:
        score (int): the score to validate

    Returns:
        bool: True if score is valid
    """
    return score >= 0 and score < 50


def list_of_names(players: List[PlayerInfo]) -> List[str]:
    """Returns a list of player names.

    Args:
        players (List[PlayerInfo): the list of players

    Returns:
        List[str]: just a list of their names
    """
    return [player.get(PlayerInfo.NAME) for player in players]


def lookup_player_name(teamroster: TeamRoster, player_id: int) -> str:
    """Look up the player's name for the given player id.

    Args:
        teamroster (TeamRoster): the team roster
        player_id (int): the id of the player to lookup

    Returns:
        str: the player name if found otherwise None
    """
    for player in teamroster.get(TeamRoster.PLAYERS):
        if player.get(PlayerInfo.ID) == player_id:
            return player.get(PlayerInfo.NAME)
    return None


def lookup_game(games: List[Game], game_id: int) -> Game:
    """Lookup the given game id in the a list of games.

    Args:
        games (List[Game]): the list of games
        game_id (int): the id of the game to find

    Returns:
        Game: the game associated with the game id
    """
    for game in games:
        if game.get(Game.ID) == game_id:
            return game
    return None


def gamesheet_overview(gamesheet: GameSheet, game: Game,
                       teamroster: TeamRoster) -> str:
    """Returns a overview of the given gamesheet.

    Args:
        gamesheet (GameSheet): the game sheet
        game (Game): the game the sheet is for
        teamroster (TeamRoster): the team roster

    Returns:
        str: the overview
    """
    score = GameSheetOverview.SCORE.value.format(
        gamesheet.get(GameSheet.SCORE))
    parts = [GameFormatter(game).format(), score]
    hrs = []
    ss = []
    for player_id in set(gamesheet.get(GameSheet.HR)):
        hrs.append("{}: {}".format(
            lookup_player_name(teamroster, player_id),
            gamesheet.get(GameSheet.HR).count(player_id)))
    for player_id in set(gamesheet.get(GameSheet.SS)):
        ss.append("{}: {}".format(
            lookup_player_name(teamroster, player_id),
            gamesheet.get(GameSheet.SS).count(player_id)))
    parts.append(GameSheetOverview.HRS.value.format("\n\t".join(hrs)))
    parts.append(GameSheetOverview.SS.value.format("\n\t".join(ss)))
    return "\n".join(parts)


def more_hr_than_rbis(game_sheet: GameSheet, hrs: int) -> bool:
    """Would adding the given homeruns mean there is more homeruns than runs.

    Args:
        game_sheet (GameSheet): the game sheet information
        hrs (int): how many homeruns that someone wants to add

    Returns:
        bool: True if there would be more homeruns than runs
    """
    proposed_hrs = len(game_sheet.get(GameSheet.HR)) + hrs
    return proposed_hrs > game_sheet.get(GameSheet.SCORE)


class SubmitScore(Action):
    """Submit the score"""
    DETERMINE_WHICH_GAME_STATE = "determine what game they want to submit"
    DETERMINE_WHICH_TEAM_STATE = "determine what team they want to submit for"
    DETERMINE_WHICH_METHOD_STATE = "determine what method to use"
    LIST_OF_STATES = [DETERMINE_WHICH_GAME_STATE,
                      DETERMINE_WHICH_TEAM_STATE,
                      DETERMINE_WHICH_METHOD_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[Player, List[Message],
                                           ActionKey]:
        """Process a message related to submitting score.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response message and
                                                     next action to take
        """
        # get the current state
        current_state = player.get_action_state().get_state()

        # if not captain or convenor send them back to home page
        if not player.is_convenor() and not player.is_captain():
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.NOT_CAPTAIN.value)
            return (player, [message], ActionKey.HOME_KEY)
        elif current_state in SubmitScoreByText.LIST_OF_STATES:
            return SubmitScoreByText(self.database,
                                     self.platform).process(player, message)
        elif current_state in SubmitScoreByButtons.LIST_OF_STATES:
            return SubmitScoreByButtons(self.database,
                                        self.platform).process(player, message)
        elif did_they_cancel(message):
            # check if they cancelled
            return (player, [], ActionKey.HOME_KEY)
        elif (current_state is None):
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
            return self.select_team(player, message)
        elif current_state == SubmitScore.DETERMINE_WHICH_GAME_STATE:
            # received some game so need try to find it
            return self.select_game(player, message)
        elif current_state == SubmitScore.DETERMINE_WHICH_METHOD_STATE:
            # determine which method they want to use
            return self.select_method(player, message)
        return (player, [], ActionKey.HOME_KEY)

    def display_games(self, player: Player,
                      message: Message) -> Tuple[Player, List[Message],
                                                 ActionKey]:
        """Display a list of games the user can submit for.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response messages and
                                                     next action to take
        """
        action_state = player.get_action_state()

        # find the team they are submitting for
        team_id = action_state.get_data().get(Team.ID, None)
        if team_id is None:
            return self.display_teams(player, message)

        # get the games (from state otherwise make the API request)
        if action_state.get_data().get(GAMES):
            games = action_state.get_data().get(GAMES)
        else:
            # get the games and remember them for later
            captain_id = action_state.get_data()\
                .get(Team.CAPTAIN).get(PlayerInfo.ID)
            games = self.platform.games_to_submit_scores_for(int(captain_id),
                                                             int(team_id))
            data = action_state.get_data()
            data[GAMES] = games
            player.set_action_state(action_state.set_data(data))

        game_options = []
        for game in games:
            option = Option(GameFormatter(game).format(),
                            str(game.get(Game.ID)))
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

    def select_game(self, player: Player,
                    message: Message) -> Tuple[Player, List[Message],
                                               ActionKey]:
        """Select the game from the given message.

        Args:
            player (Player): the player selecting the game
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response messages and
                                                     next action to take
        """
        # get the game id from the message payload or
        # parse it out of the message
        if message.get_payload() is not None:
            game_id = message.get_payload().get_options()[0].get_data()
        else:
            game_id = parse_number(message.get_message())

        # TODO: try to figure out the game based upon the message
        # still need to figure out the game
        if (game_id is None or
                not is_game_in_list_of_games(
                    game_id,
                    player.get_action_state().get_data().get(GAMES))):

            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.UNRECOGNIZED_GAME.value)
            (player, messages, next_action) = self.display_games(player,
                                                                 message)
            return (player, [message] + messages, next_action)

        # remember the game id for later
        action_state = player.get_action_state()
        action_state.set_state(SubmitScore.DETERMINE_WHICH_METHOD_STATE)
        data = action_state.get_data()
        data[Game.ID] = game_id
        player.set_action_state(action_state.set_data(data))

        return self.display_methods(player, message)

    def display_teams(self, player: Player,
                      message: Message) -> Tuple[Player, List[Message],
                                                 ActionKey]:
        """Display the list of teams the user can submit scores for.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response messages and
                                                     next action to take
        """

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
                if player.is_captain(team_id=team.get(Team.ID)):
                    team_name = get_team_name(team)
                    team_options.append(Option(team_name,
                                               str(team.get(Team.ID))))
                    team_lookup[str(team.get(Team.ID))] = team_name

        if (len(team_options) == 0):
            # no teams to display
            message = Message(message.get_sender_id(),
                              recipient_id=message.get_recipient_id(),
                              message=ScoreSubmission.NOT_CAPTAIN.value)
            return (player, [message], ActionKey.HOME_KEY)

        # sort the teams alphbetically
        team_options.sort(key=lambda option: option.get_title())

        # remember for later in case they write out the team name
        state = player.get_action_state()
        data = state.get_data()
        data[TEAM_LOOKUP] = team_lookup
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

    def select_team(self, player: Player,
                    message: Message) -> Tuple[Player, List[Message],
                                               ActionKey]:
        """Try to select the team from the given message.

        Args:
            player (Player): the player that is selecting the team
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response message and
                                                     next action to take
        """
        # get the team id from the message payload or
        # parse it out of the message
        if message.get_payload() is not None:
            team_id = message.get_payload().get_options()[0].get_data()
        else:
            team_id = parse_number(message.get_message())
        action_state = player.get_action_state()
        team_keys = action_state.get_data().get(TEAM_LOOKUP, {}).keys()

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

    def display_methods(self, player: Player,
                        message: Message) -> Tuple[Player, List[Message],
                                                   ActionKey]:
        """Display the various methods that can be used to submit.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response messages and
                                                     next action to take
        """
        method_options = []
        method_options.append(Option(ScoreSubmission.TEXT_METHOD.value,
                                     ScoreSubmission.TEXT_METHOD.value))
        method_options.append(Option(ScoreSubmission.BUTTON_METHOD.value,
                                     ScoreSubmission.BUTTON_METHOD.value))
        # add a cancel option
        method_options.append(Option(ScoreSubmission.CANCEL.value,
                                     ScoreSubmission.CANCEL.value))

        # update player state
        action_state = player.get_action_state()
        player.set_action_state(
            action_state.set_state(SubmitScore.DETERMINE_WHICH_METHOD_STATE))

        # send them a list of games they can select
        payload = Payload(options=method_options)
        return (player,
                [Message(message.get_sender_id(),
                         recipient_id=message.get_recipient_id(),
                         message=ScoreSubmission.WHICH_METHOD.value,
                         payload=payload)],
                None)

    def select_method(self, player: Player,
                      message: Message) -> Tuple[Player, List[Message],
                                                 ActionKey]:
        """Select the submission method from the message.

        Args:
            player (Player): the player who selected the method
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                          response message and
                                                          next action to take
        """
        # check if they cancelled
        if did_they_cancel(message):
            return (player, [], ActionKey.HOME_KEY)

        # try to determine what method they used
        if message.get_payload() is not None:
            method = message.get_payload().get_options()[0].get_data()
        else:
            method = message.get_message()

        method = "" if method is None else method.lower().strip()
        if method == ScoreSubmission.TEXT_METHOD.value or "message" in method:
            action_state = player.get_action_state()
            player.set_action_state(
                action_state.set_state(SubmitScoreByText.INITIAL_STATE))
            return SubmitScoreByText(self.database,
                                     self.platform).process(player, message)
        elif (method == ScoreSubmission.BUTTON_METHOD.value or
                "button" in method):
            action_state = player.get_action_state()
            player.set_action_state(
                action_state.set_state(SubmitScoreByButtons.INITIAL_STATE))
            return SubmitScoreByButtons(self.database,
                                        self.platform).process(player, message)

        # have no idea what method they are using
        (player, messages, next_action) = self.display_methods(player, message)
        content = ScoreSubmission.UNRECOGNIZED_METHOD.value
        unknown_message = Message(message.get_sender_id(),
                                  recipient_id=message.get_recipient_id(),
                                  message=content)
        return (player, [unknown_message] + messages, next_action)

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
        data[TEAM_LOOKUP] = {str(team_id): "only one team"}
        data[Team.ID] = team_id
        roster = self.platform.lookup_team_roster(team_id)
        data[TEAM_ROSTER] = roster
        data[Team.CAPTAIN] = who_is_captain(data[TEAM_ROSTER])
        player.set_action_state(state.set_data(data))
        return player


class SubmitScoreByText(Action):
    INITIAL_STATE = "starting to submit score by text"
    REVIEW_DETAILS_STATE = "reviewing details"
    LIST_OF_STATES = [INITIAL_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[Player, List[Message],
                                           ActionKey]:
        """Process a message related to submitting score by simple message.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the update player,
                                                     response messages and
                                                     next action to take
        """
        to_do = Message(message.get_sender_id(),
                        recipient_id=message.get_recipient_id(),
                        message=ScoreSubmission.NOT_DONE.value)
        return (player, [to_do], ActionKey.HOME_KEY)


class SubmitScoreByButtons(Action):
    INITIAL_STATE = "starting to submit score by button"
    DETERMINE_SCORE_STATE = "what was the score of the game"
    DETERMINE_SS_BATTER_STATE = "who hit a ss"
    DETERMINE_SS_NUMBER_STATE = "how many ss did they hit"
    DETERMINE_HR_BATTER_STATE = "who hit a hr"
    DETERMINE_HR_NUMBER_STATE = "how many hr did they hit"
    REVIEW_DETAILS_STATE = "reviewing details"
    LIST_OF_STATES = [INITIAL_STATE, DETERMINE_SCORE_STATE,
                      DETERMINE_SS_BATTER_STATE, DETERMINE_SS_NUMBER_STATE,
                      DETERMINE_HR_BATTER_STATE, DETERMINE_HR_NUMBER_STATE,
                      REVIEW_DETAILS_STATE]

    def process(self, player: Player,
                message: Message) -> Tuple[Player, List[Message],
                                           ActionKey]:
        """Process a message related to submitting score using buttons.

        Args:
            player (Player): the player to display methods for
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response messages and
                                                     next action to take
        """
        state = player.get_action_state().get_state()
        if state == SubmitScoreByButtons.INITIAL_STATE:
            player = init_gamesheet(player)
            return self.ask_for_score(player, message)
        elif state == SubmitScoreByButtons.DETERMINE_SCORE_STATE:
            return self.set_score(player, message)
        elif state == SubmitScoreByButtons.DETERMINE_SS_BATTER_STATE:
            return self.select_batter(player, message, GameSheet.SS)
        elif state == SubmitScoreByButtons.DETERMINE_SS_NUMBER_STATE:
            return self.set_category_number(player, message, GameSheet.SS)
        elif state == SubmitScoreByButtons.DETERMINE_HR_BATTER_STATE:
            return self.select_batter(player, message, GameSheet.HR)
        elif state == SubmitScoreByButtons.DETERMINE_HR_NUMBER_STATE:
            return self.set_category_number(player, message, GameSheet.HR)
        elif state == SubmitScoreByButtons.REVIEW_DETAILS_STATE:
            return self.submit_game_sheet(player, message)
        return (player, [], ActionKey.HOME_KEY)

    def ask_for_score(self, player: Player,
                      message: Message) -> Tuple[Player, List[Message],
                                                 ActionKey]:
        """Ask the player for the score of their game

        Args:
            player (Player): the player who will be asked
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response messages and
                                                     next action to take
        """
        # set the state
        action_state = player.get_action_state()
        player.set_action_state(
            action_state.set_state(SubmitScoreByButtons.DETERMINE_SCORE_STATE))

        # give a list of quick reply options
        scores = [Option(number, str(number)) for number in range(1, 3)]
        scores.append(Option(ScoreSubmission.CANCEL.value,
                             ScoreSubmission.CANCEL.value))
        payload = Payload(payload_type=Payload.QUICK_REPLY_TYPE,
                          options=scores)
        message = Message(message.get_sender_id(),
                          recipient_id=message.get_recipient_id(),
                          message=ScoreSubmission.ASK_FOR_SCORE.value,
                          payload=payload)
        return (player, [message], None)

    def set_score(self, player: Player,
                  message: Message) -> Tuple[Player, List[Message],
                                             ActionKey]:
        """Set the score from the person message

        Args:
            player (Player): the player who gave their score
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response messages and
                                                     next action to take
        """
        if did_they_cancel(message):
            return (player, [], ActionKey.HOME_KEY)

        if message.get_payload() is not None:
            score = int(message.get_payload().get_options()[0].get_data())
        else:
            score = parse_number(message.get_message())
        if score is not None and is_score_valid(score):
            # set the score of the game
            action_state = player.get_action_state()
            data = action_state.get_data()
            data[GAME_SHEET][GameSheet.SCORE] = score
            action_state.set_data(data)
            player.set_action_state(action_state)
            return self.display_batters(player, message, GameSheet.HR)
        else:
            return self.ask_for_score(player, message)

    def display_batters(self, player: Player, message: Message,
                        category: str) -> Tuple[Player, List[Message],
                                                ActionKey]:
        """Display a list of players to choose from.

        Args:
            message (Message): the message received
            player (Player): the captain or the convenor
            category (str): the category display players for.

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                          response message and
                                                          next action to take
        """
        # update the state
        action_state = player.get_action_state()
        state = (SubmitScoreByButtons.DETERMINE_HR_BATTER_STATE
                 if category == GameSheet.HR
                 else SubmitScoreByButtons.DETERMINE_SS_BATTER_STATE)
        player.set_action_state(action_state.set_state(state))

        # setup each player as a button to click
        data = player.get_action_state().get_data()
        batters = []
        if category == GameSheet.SS or not more_hr_than_rbis(
                data.get(GAME_SHEET), 1):
            # only show batters if homeruns is less than score
            # otherwise can assume they are done
            for teammate in data.get(TEAM_ROSTER).get(TeamRoster.PLAYERS):
                if player_eligible_for_category(data.get(GAME_SHEET), teammate,
                                                category):
                    batters.append(Option(teammate.get(PlayerInfo.NAME),
                                          str(teammate.get(PlayerInfo.ID))))

        # add the cancel and done option so they can proceed
        done = ScoreSubmission.DONE.value
        cancel = ScoreSubmission.CANCEL.value
        batters.append(Option(done, done))
        batters.append(Option(cancel, cancel))

        # create the message with each batter as a payload option
        payload = Payload(options=batters)
        m = (ScoreSubmission.HR_SELECT_PLAYER.value
             if category == GameSheet.HR
             else ScoreSubmission.SS_SELECT_PLAYER.value)
        message = Message(message.get_sender_id(),
                          recipient_id=message.get_recipient_id(),
                          message=m,
                          payload=payload)
        return (player, [message], None)

    def select_batter(self, player: Player, message: Message,
                      category: str) -> Tuple[Player, List[Message],
                                              ActionKey]:
        """Select a batter on the team

        Args:
            player (Player): [description]
            message (Message): [description]
            category (str): [description]

        Returns:
            Tuple[Player, List[Message], ActionKey]: [description]
        """
        # check if they cancelled or are done
        if did_they_cancel(message):
            return (player, [],  ActionKey.HOME_KEY)
        elif are_they_done(message):
            return (self.display_review(player, message)
                    if category == GameSheet.SS
                    else self.display_batters(player, message, GameSheet.SS))
        batter_id = None
        if message.get_payload() is not None:
            batter_id = int(message.get_payload().get_options()[0].get_data())
        else:
            data = player.get_action_state().get_data()
            team_roster = data.get(TEAM_ROSTER)
            (confidence, batters) = match_with_player(
                message.get_message(), team_roster.get(TeamRoster.PLAYERS))
            confident = confidence < CONFIDENCE_LEVEL
            if len(batters) != 1 or confident:
                # if unable to narrow down to one players let them know why
                # and ask again
                no_player = ScoreSubmission.UNRECOGNIZED_PLAYER.value
                mutliple_players = ScoreSubmission.AMBIGUOUS_PLAYER.value
                content = (no_player if len(batters) <= 1 or confident
                           else mutliple_players.format(
                                " and ".join(list_of_names(batters))))
                message = Message(message.get_sender_id(),
                                  recipient_id=message.get_recipient_id(),
                                  message=content)
                (player, messages,
                    next_action) = self.display_batters(player, message,
                                                        category)
                return (player, [message] + messages, next_action)
            elif not player_eligible_for_category(data.get(GAME_SHEET),
                                                  batters[0],
                                                  category):
                content = ScoreSubmission.PLAYER_NOT_ELIGIBLE.value
                message = Message(message.get_sender_id(),
                                  recipient_id=message.get_recipient_id(),
                                  message=content)
                (player, messages,
                    next_action) = self.display_batters(player, message,
                                                        category)
                return (player, [message] + messages, next_action)

            batter_id = batters[0].get(PlayerInfo.ID)

        roster = player.get_action_state().get_data().get(TEAM_ROSTER)
        if (batter_id is not None and
                lookup_player_name(roster, batter_id) is not None):
            # set the score of the game
            action_state = player.get_action_state()
            data = action_state.get_data()
            data[BATTER_ID] = batter_id
            action_state.set_data(data)
            player.set_action_state(action_state)
            return self.ask_for_category_number(player, message, category)
        else:
            return self.display_batters(player, message)

    def ask_for_category_number(self, player: Player, message: Message,
                                category: str) -> Tuple[Player, List[Message],
                                                        ActionKey]:
        """Ask for the number of hits for the given category

        Args:
            player (Player): the player to ask
            message (Message): the message received
            category (str): the category to ask about

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response message and
                                                     next action to take
        """
        # update the state
        action_state = player.get_action_state()
        state = (SubmitScoreByButtons.DETERMINE_HR_NUMBER_STATE
                 if category == GameSheet.HR
                 else SubmitScoreByButtons.DETERMINE_SS_NUMBER_STATE)
        player.set_action_state(action_state.set_state(state))

        # set a list of numbers
        hits = [Option(number, str(number)) for number in range(1, 6)]
        hits.append(Option(ScoreSubmission.CANCEL.value,
                           ScoreSubmission.CANCEL.value))
        payload = Payload(payload_type=Payload.QUICK_REPLY_TYPE, options=hits)

        # specify who the batter was the selected in case they picked wrong one
        data = action_state.get_data()
        player_name = lookup_player_name(data.get(TEAM_ROSTER),
                                         data.get(BATTER_ID))
        how_many = ScoreSubmission.HOW_HITS_PLAYER.value.format(player_name)
        message = Message(message.get_sender_id(),
                          recipient_id=message.get_recipient_id(),
                          message=how_many,
                          payload=payload)
        return (player, [message], None)

    def set_category_number(self, player: Player, message: Message,
                            category: str) -> Tuple[Player, List[Message],
                                                    ActionKey]:
        """Set the number of hits based upon the message received

        Args:
            player (Player): the player
            message (Message): the message received
            category (str): the category of hits

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response messages and
                                                     next action to take
        """

        if did_they_cancel(message) or are_they_done(message):
            # check if they cancelled or are done
            return self.display_batters(player, message, category)

        # try get the number of hits out of the messge
        if message.get_payload() is not None:
            hits = int(message.get_payload().get_options()[0].get_data())
        else:
            hits = parse_number(message.get_message())

        action_state = player.get_action_state()
        data = action_state.get_data()
        game_sheet = player.get_action_state().get_data().get(GAME_SHEET)
        if (hits is not None and (category == GameSheet.SS or
                                  not more_hr_than_rbis(game_sheet, hits))):
            # set the score of the game
            batter_id = data.get(BATTER_ID)
            data[GAME_SHEET][category] += [batter_id for hit in range(0, hits)]
            action_state.set_data(data)
            player.set_action_state(action_state)
            return self.display_batters(player, message, category)
        else:
            return self.ask_for_category_number(player, message, category)

    def display_review(self, player: Player,
                       message: Message) -> Tuple[Player, List[Message],
                                                  ActionKey]:
        """Display the review of their game sheet.

        Args:
            player (Player): player submitting the socre
            message (Message): the message received

        Returns:
            Tuple[Player, List[Message], ActionKey]: the updated player,
                                                     response messages and
                                                     next action to take
        """

        # update the state
        action_state = player.get_action_state()
        player.set_action_state(action_state.set_state(
            SubmitScoreByButtons.REVIEW_DETAILS_STATE))

        # format an overview of the game sheet they have created
        data = action_state.get_data()
        gamesheet = data.get(GAME_SHEET)
        game = lookup_game(data.get(GAMES), int(data.get(Game.ID)))
        teamroster = data.get(TEAM_ROSTER)
        overview = gamesheet_overview(gamesheet, game, teamroster)

        # add some quick replies
        options = []
        options.append(Option(ScoreSubmission.SUBMIT.value,
                              ScoreSubmission.SUBMIT.value))
        options.append(Option(ScoreSubmission.CANCEL.value,
                              ScoreSubmission.CANCEL.value))
        payload = Payload(payload_type=Payload.QUICK_REPLY_TYPE,
                          options=options)

        message = Message(message.get_sender_id(),
                          recipient_id=message.get_recipient_id(),
                          message=overview,
                          payload=payload)
        return (player, [message], None)

    def submit_game_sheet(self, player: Player,
                          message: Message) -> Tuple[Player, List[Message],
                                                     ActionKey]:
        """Submit the game sheet summary unless cancel.

        Args:
            player (Player): [description]
            message (Message): [description]

        Returns:
            Tuple[Player, List[Message], ActionKey]: [description]
        """
        if did_they_cancel(message):
            return (player, [], ActionKey.HOME_KEY)
        elif did_they_submit(message):
            game_sheet = player.get_action_state().get_data().get(GAME_SHEET)
            try:
                self.platform.submit_game_sheet(game_sheet)
                content = ScoreSubmission.GAME_SUBMITTED.value
                return (player,
                        [Message(message.get_sender_id(),
                                 recipient_id=message.get_recipient_id(),
                                 message=content)],
                        ActionKey.HOME_KEY)
            except (GameDoesNotExist, NotCaptainException):
                content = ScoreSubmission.UNRECONVERABLE_ERROR.value
                return (player,
                        [Message(message.get_sender_id(),
                                 recipient_id=message.get_recipient_id(),
                                 message=content)],
                        ActionKey.HOME_KEY)
            except PlatformException:
                # give them the option to try again since
                # possible just a network error
                content = Message(
                    message.get_sender_id(),
                    recipient_id=message.get_recipient_id(),
                    message=ScoreSubmission.COMMUNICATION_ERROR.value)
                (player, messages,
                    next_action) = self.display_review(player, message)
                return (player, [content] + messages, next_action)
