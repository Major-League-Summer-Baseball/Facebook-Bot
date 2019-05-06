'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds an implementation of the interaction witht the platform
'''
import requests
from api.logging import LOGGER
from api.errors import PlatformException,\
    PLATFORMMESSAGE, NotCaptainException, IdentityException,\
    BatterException
from api.variables import HEADERS, BASEURL


class PlatformService():

    def lookup_player(self, name):
        """Returns a lookup for the player in the league

        Parameter:
            name: the name of the player to lookup (str)
        Raises:
            PlatformException: if platform gives an error
        Returns:
            player: None if can't determine player otherwise a player object
        """
        submission = {"player_name": name, "active": 1}
        response = requests.post(BASEURL + "api/view/player_lookup",
                                 params=submission,
                                 headers=HEADERS)
        players = response.json()
        if (response.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        if len(players) == 0 or len(players) > 1:
            player_info = None
        else:
            # information was found about the player
            player_info = players[0]
        return player_info

    def lookup_player_email(self, email):
        """Returns a lookup for a player in the league using their email provided

        Parameters:
            user: the user dictionary (dict)
            email: the email they given (string)
        Raises:
            IdentityException: if no one is found
        Returns:
            player_info: the player info from MLSB
        """
        submission = {"email": email}
        response = requests.post(BASEURL + "api/view/player_lookup",
                          params=submission,
                          headers=HEADERS)
        if response.status_code != 200:
            raise PlatformException(PLATFORMMESSAGE)
        players = response.json()
        if len(players) == 0:
            raise IdentityException("Not sure who you are, ask admin")
        return players[0]

    def is_player_captain(self, player):
        """Updates a player_info and checks if they are a captain

        Parameters:
            player: the player (Player)
        Returns:
            captain: a list of team they are the captain for
        """
        player_id = player.get_player_id()
        params = {"player_id": player_id}
        response = requests.post(BASEURL + "api/view/players/team_lookup",
                                 params=params,
                                 headers=HEADERS)
        if (response.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        # now look up teams
        captain = []
        teams = response.json()
        for team in teams:
            if (team['captain'] is not None and
                    team['captain']['player_id'] == player_id):
                captain.append(team["team_id"])
        return captain

    def get_upcoming_games(player):
        """Returns league leaders for some stat

        Parameters:
            player: the player (Player)
        Returns:
            a list of upcoming games
        """
        player_id = player.get_player_id()
        params = {"player_id": player_id}
        response = requests.post(BASEURL + "api/bot/upcoming_games",
                                 data=params,
                                 headers=HEADERS)
        if (response.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()
