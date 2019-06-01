'''
@author: Dallas Fraser
@author: 2019-05-23
@organization: MLSB
@project: Facebook Bot
@summary: welcome new player, registers the players to their teams
'''
from api.helper import get_this_year
from api.message import Message
from api.logging import LOGGER
from api.settings.action_keys import HOME_KEY
from api.settings.message_strings import ACKNOWLEDGE_CONVENOR, PART_OF_TEAM,\
    ACKNOWLEDGE_CAPTAIN
from api.actions import Action, ActionState


class WelcomeUser(Action):
    """
        Welcome the user to the league, find out what teams they are on and
        subscribe them. Also, determine if they are captain or convenor.
    """

    def process(self, message, action_map):
        """
            The main entry point

            Notes:
                Use the player email to check whether they are convenor
                    assuming web master will update this
                Check if they are a captain
                Otherwise just subscribe them to their teams
        """
        self.message = message
        self.action_map = action_map
        messenger_id = self.message.get_sender_id()
        recipient_id = self.message.get_recipient_id()
        player = self.database.get_player(messenger_id)

        # determine if they are a convenor
        if self.is_player_convenor(player):
            LOGGER.debug("Welcoming a convenor (this is a big deal)")
            m1 = Message(messenger_id,
                         message=ACKNOWLEDGE_CONVENOR,
                         recipient_id=recipient_id)
            self.messenger.send_message(m1)
            player.make_convenor()
            teams = self.platform.lookup_all_teams()
            LOGGER.debug(teams)
            for team_id in teams.keys():
                player.add_team({"team_id": team_id})
                player.make_captain({"team_id": team_id})
        else:
            # add the players to their teams and if they captain make them
            # a captain
            teams = self.platform.lookup_teams_player_associated_with(player)
            LOGGER.debug(teams)
            current_year = get_this_year()
            for team in teams:
                # adding the player to the team will subscribe them
                year = team.get('year', None)
                if year is not None and year == current_year:
                    team_name = team.get("team_name", team.get("color",
                                                               "name unknown"))
                    m1 = Message(messenger_id,
                                 message=PART_OF_TEAM.format(team_name),
                                 recipient_id=recipient_id)
                    self.messenger.send_message(m1)
                    player.add_team(team)
                    if self.is_player_captain_of_team(player, team):
                        m1 = Message(messenger_id,
                                     message=ACKNOWLEDGE_CAPTAIN,
                                     recipient_id=recipient_id)
                        self.messenger.send_message(m1)
                        player.make_captain(team)
        self.successful(player)

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
        LOGGER.info("Welcomed player: " + str(player))

        return self.initiate_action(self.message,
                                    self.action_map,
                                    HOME_KEY,
                                    player)
