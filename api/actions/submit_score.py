'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: Action for when a captain/convenor submits a score
'''
from api.logging import LOGGER
from api.parsers import parse_number
from api.helper import convert_to_int, is_game_in_list_of_games
from api.settings.action_keys import HOME_KEY
from api.actions import Action
from api.message import Message, Option, Payload, GameFormatter
from api.settings.message_strings import NOT_CAPTAIN_COMMENT,\
    SUBMIT_SCORE_USING_BUTTONS_TITLE, SUBMIT_SCORE_BY_TEXT_TITLE,\
    SELECT_TEAM_TO_SUBMIT_FOR_COMMENT, NO_GAME_TO_SUBMIT,\
    SELECT_GAME_TO_SUBMIT_COMMENT, UNRECOGNIZED_GAME, UNRECOGNIZED_TEAM


class SubmitScore(Action):
    """Submit the score"""
    DETERMINE_WHICH_GAME_STATE = "Determine what game they want to submit"
    DETERMINE_WHICH_TEAM_STATE = "Determine what team they want to submit for"
    ASK_METHOD_STATE = "What method would they like to use"

    def process(self, message, action_map):
        """Determine which method to use (by text or by buttons)"""
        self.action_map = action_map
        self.message = message

        self.player = self.database.get_player(self.message.get_sender_id())
        if not self.player.is_convenor() and not self.player.is_captain():
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=NOT_CAPTAIN_COMMENT)
            self.messenger.send_message(message)
            self.initiate_action(self.message,
                                 action_map,
                                 HOME_KEY,
                                 self.player)
        current_state = self.player.get_action_state().get_state()
        if (current_state is None):

            if (self.player.is_convenor() or
                    len(self.player.get_teams_captain()) > 1):

                # determine what team they want to submit a game for
                self.display_teams()
            else:

                # need to find what game they want to submit for
                team_id = str(self.player.get_teams_captain()[0])
                self.save_data("teams_lookup", {str(team_id): "only one team"})
                self.select_team(team_id)
                self.display_games()
        elif current_state == SubmitScore.DETERMINE_WHICH_TEAM_STATE:

            # received some team they picked
            self.parse_team()
        elif current_state == SubmitScore.FIND_GAME_STATE:

            # received some game so need try to find it
            self.parse_game()
        elif current_state == SubmitScore.ASK_METHOD_STATE:

            # determine which method they want to use
            self.display_methods()
        elif current_state in SubmitScoreByText.BY_TEXT_STATES:
            action = SubmitScoreByText(self.database,
                                       self.platform,
                                       self.messenger)
            action.process(message, action_map)
        elif current_state in SubmitScoreByButtons.BY_BUTTONS_STATES:
            action = SubmitScoreByButtons(self.database,
                                          self.platform,
                                          self.messenger)
            action.process(message, action_map)

    def display_games(self):
        """Display the games"""
        action_state = self.player.get_action_state()

        # find the team they are submitting for
        team_id = action_state.get_data().get("team_id", None)
        if team_id is None:
            self.display_teams()
            return

        # get the games (from state otherwise make the API request)
        if action_state.get_data().get("games"):
            games = self.player.get_action_state().get_data().get("games")
        else:
            games = self.platform.games_to_submit_scores_for(self.player,
                                                             team_id)
            # remember them for later
            self.save_data("games", games)

        game_options = []
        for game in games:
            option = Option(GameFormatter(game).format(),
                            str(game.get("game_id")))
            game_options.append(option)

        if len(game_options) == 0:
            # return to home screen since no games to submit for
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=NO_GAME_TO_SUBMIT)
            self.messenger.send_message(message)
            return self.initiate_action(self.message,
                                        self.action_map,
                                        HOME_KEY,
                                        self.player)

        # send them a list of games they can select
        payload = Payload(options=game_options)
        message = Message(self.message.get_sender_id(),
                          recipient_id=self.message.get_recipient_id(),
                          message=SELECT_GAME_TO_SUBMIT_COMMENT,
                          payload=payload)
        self.messenger.send_message(message)

        # update player state
        self.update_state(SubmitScore.DETERMINE_WHICH_GAME_STATE)

    def display_methods(self):
        pass

    def display_teams(self):
        """Displays the list of teams they can select to pick from"""

        # get the teams the player can submit scores for
        team_options = []
        team_lookup = {}
        if self.player.is_convenor():
            teams = self.platform.lookup_all_teams()
            for team_id, team_name in teams.items():
                team_lookup[str(team_id)] = team_name
                team_options.append(Option(team_name,
                                           str(team_id)))
        else:
            teams = self.platform.lookup_teams_player_associated_with(
                self.player)
            for team in teams:
                team_name = team.get("team_name",
                                     team.get("color", "name unknown"))
                team_options.append(Option(team_name,
                                           str(team.get("team_id"))))
                team_lookup[str(team.get("team_id"))] = team_name

        # sort the teams alphbetically
        team_options.sort(key=lambda option: option.get_title())

        # remember for later in case they write out the team name
        self.save_data("teams_lookup", team_lookup)

        # send them a list of teams they can select
        payload = Payload(options=team_options)
        message = Message(self.message.get_sender_id(),
                          recipient_id=self.message.get_recipient_id(),
                          message=SELECT_TEAM_TO_SUBMIT_FOR_COMMENT,
                          payload=payload)
        self.messenger.send_message(message)

        # update player state
        self.update_state(SubmitScore.DETERMINE_WHICH_TEAM_STATE)

    def parse_team(self):
        """Parse the team response"""
        if self.message.get_payload() is not None:
            self.select_team(
                self.message.get_payload().get_options()[0].get_data())
        else:
            self._parse_team_helper(self.message.get_message())

    def _parse_team_helper(self, message_text):
        if message_text is None:
            return
        team_id = convert_to_int(message_text)
        if team_id is None:

            # TODO: try to figure out the team based upon the message
            # still need to figure out the team
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=UNRECOGNIZED_TEAM)
            self.messenger.send_message(message)
            self.display_teams()
            return
        self.select_team(team_id)

    def parse_game(self):
        """Parses the game response"""
        if self.message.get_payload() is not None:
            self.select_game(
                self.message.get_payload().get_options()[0].get_data())
        else:
            self._parse_team_helper(self.message.get_message())

    def _parse_game_helper(self, message_text):
        game_id = convert_to_int(message_text)
        if game_id is None:
            # TODO: try to figure out the game based upon the message
            # still need to figure out the game
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=UNRECOGNIZED_GAME)
            self.messenger.send_message(message)
            self.display_games()
            return
        self.select_game(game_id)

    def select_game(self, game_id):
        """Updates the state information to use the given game"""

        # check if game id is valid
        action_state = self.player.get_action_state()
        data = action_state.get_data()
        if not is_game_in_list_of_games(game_id, data.get("games")):

            # still need to figure out the game
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=UNRECOGNIZED_GAME)
            self.messenger.send_message(message)
            self.display_games()
            return

        # remember the game id for later
        self.save_data("game_id", game_id)
        # for now assuming what method they want to use
        action = SubmitScoreByButtons(self.database,
                                      self.platform,
                                      self.messenger)
        action.process(self.message, self.action_map)

    def select_team(self, team_id):
        """Update the state information to use the given team"""

        # check if team id is valid
        action_state = self.player.get_action_state()
        data = action_state.get_data()
        if team_id not in data.get("teams_lookup").keys():

            # still need to figure out the team
            message = Message(self.message.get_sender_id(),
                              recipient_id=self.message.get_recipient_id(),
                              message=UNRECOGNIZED_TEAM)
            self.messenger.send_message(message)
            self.display_teams()
            return

        # remember the team id and team roster
        self.save_data("team_id", team_id)
        self.save_data("teamroster", self.platform.lookup_team_roster(team_id))

        # now determine what game the want to submit for
        self.display_games()

    def update_state(self, state):
        """Updates the players state"""
        action_state = self.player.get_action_state()
        action_state.set_state(state)
        self.player.set_action_state(action_state)
        self.database.save_player(self.player)

    def save_data(self, key, information):
        """Add the given Helper method for saving data"""
        action_state = self.player.get_action_state()
        data = action_state.get_data()
        data[key] = information
        action_state.set_data(data)
        self.player.set_action_state(action_state)
        self.database.save_player(self.player)


class SubmitScoreByText(Action):
    INITIAL_STATE = ""
    BY_TEXT_STATES = []

    def process(self, message, action_map):
        self.action_map = action_map
        self.message = message


class SubmitScoreByButtons(Action):
    BY_BUTTONS_STATES = []

    def process(self, message, action_map):
        self.action_map = action_map
        self.message = message
