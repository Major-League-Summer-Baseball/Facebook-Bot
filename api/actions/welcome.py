'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: welcome new player, registers the players to their teams
'''
from api.logging import LOGGER
from api.settings.action_keys import HOME_KEY
from api.actions import ActionInterface, ActionState


class WelcomeAction(ActionInterface):

    def process(self, action_map):
        self.action_map = action_map
        messenger_id = self.message.get_sender_id()
        player = self.database.get_player(messenger_id)

        # determine if they are a convenor
        if self.is_player_convenor(player):
            player.make_convenor()
        else:
            # add the players to their teams and if they captain make them
            # a captain
            teams = self.platform.lookup_teams_player_associated_with()
            for team in teams:
                # adding the player to the team will subscribe them
                player.add_team(team)
                if self.is_player_captain_of_team(player, team):
                    player.make_captain(team)

    def is_player_convenor(self, player):
        """Returns True if the player is a convenor, otherwise False"""
        convenor_list = self.database.get_convenor_email_list()
        email = player.get_player_info().get("email", None)
        is_convenor = False
        if email is not None and email in convenor_list:
            is_convenor = True
        return is_convenor

    def is_player_captain_of_team(self, player, team):
        """Returns True if player is captain of the given team

        Parameters:
            player: the player (Player)
            team: the team (dictionary)
        Returns:
            True if player is captain, otherwise False
        """
        team_captain = team.get('captain', None)
        is_captain = False
        if (team_captain is not None and
                player.get_player_id() == team_captain.get("player_id", None)):
            is_captain = True
        return is_captain

    def successful(self, player):
        """The method called when welcome action was successfully completed"""
        LOGGER.info("Identified player: " + str(player))

        # update the player for the next action
        player.set_action_state(ActionState(key=HOME_KEY))

        self.database.save_player(player)

        # proceed to complete next action
        next_action = self.action_map[HOME_KEY]
        return next_action(self.database,
                           self.platform,
                           self.messenger,
                           self.message).process(self.action_map)
