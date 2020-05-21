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
from api.players.player import Player
from api.settings.message_strings import Registration
from api.actions import ActionKey
from api.actions.action import Action


class WelcomeUser(Action):
    """
        Welcome the user to the league, find out what teams they are on and
        subscribe them. Also, determine if they are captain or convenor.
    """

    def process(self, player: Player, message: Message):
        """
            The main entry point

            Notes:
                Use the player email to check whether they are convenor
                    assuming web master will update this
                Check if they are a captain
                Otherwise just subscribe them to their teams
        """
        # send them a message - welcoming them to the league
        welcome = Registration.WELCOME.value.format(player.get_name())
        messages = [Message(message.get_sender_id(), message=welcome)]

        # determine if they are a convenor
        if self.is_player_convenor(player):
            LOGGER.debug("Welcoming a convenor (this is a big deal)")
            messages.append(Message(message.get_sender_id(),
                            message=Registration.WELCOME_CONVENOR.value,
                            recipient_id=message.get_recipient_id()))
            player.make_convenor()
            teams = self.platform.lookup_all_teams()
            LOGGER.debug(teams)
            for team_id in teams.keys():
                LOGGER.debug(f"Team id: {team_id}")
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
                    on_team = Registration.ON_TEAM.value.format(team_name)
                    messages.append(
                        Message(message.get_sender_id(),
                                message=on_team,
                                recipient_id=message.get_recipient_id()))
                    player.add_team(team)
                    if self.is_player_captain_of_team(player, team):
                        content = Registration.WELCOME_CAPTAIN.value
                        messages.append(
                            Message(message.get_sender_id(),
                                    message=content,
                                    recipient_id=message.get_recipient_id()))
                        player.make_captain(team)
        return (player, messages, ActionKey.HOME_KEY)

    def is_player_convenor(self, player: Player) -> bool:
        """Returns whether the given player is a convenor or not

        Args:
            player (Player): the player to check

        Returns:
            bool: True if convenor otherwise False
        """
        convenor_list = self.database.get_convenor_name_list()
        name = player.get_player_info().get("player_name", None)
        return name is not None and name in convenor_list

    def is_player_captain_of_team(self, player: Player, team: dict) -> bool:
        """Returns whether the player is the captain of the given team

        Args:
            player (Player): the player to see if captain
            team (dict): the team to check against

        Returns:
            bool: True if player is the captain otherwise False
        """
        player_id = player.get_player_id()
        team_captain = team.get('captain', None)
        return (team_captain is not None and
                player_id == team_captain.get("player_id", ""))
