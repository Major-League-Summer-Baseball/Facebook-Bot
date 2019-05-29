'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds an implementation of the interaction with the MLSB platform
'''
import requests
from datetime import date
from api.helper import get_this_year
from api.logging import LOGGER
from api.errors import PlatformException,\
    PLATFORMMESSAGE, IdentityException


class PlatformService():

    def __init__(self, headers, baseurl):
        self.headers = headers
        self.baseurl = baseurl

    def lookup_player_by_name(self, name):
        """Returns a lookup for the player in the league

        Parameter:
            name: the name of the player to lookup (str)
        Raises:
            PlatformException: if platform gives an error
        Returns:
            player: None if can't determine player otherwise a player object
        """
        submission = {"player_name": name, "active": 1}
        response = requests.post(self.baseurl + "api/view/player_lookup",
                                 params=submission,
                                 headers=self.headers)
        players = response.json()
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        if len(players) == 0 or len(players) > 1:
            player_info = None
        else:
            # information was found about the player
            player_info = players[0]
            LOGGER.debug("Found player information for {}".format(name))
            LOGGER.debug(player_info)
        return player_info

    def lookup_player_by_email(self, email):
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
        response = requests.post(self.baseurl + "api/view/player_lookup",
                                 params=submission,
                                 headers=self.headers)
        if response.status_code != 200:
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        players = response.json()
        if len(players) == 0:
            LOGGER.debug(
                "{} not associated with anyone in the league".format(email))
            raise IdentityException("Not sure who you are, ask admin")
        return players[0]

    def lookup_teams_player_associated_with(self, player):
        """Returns a list of teams that the given player is associated with

        Parameters:
            player: the player (Player)
        Returns:
            teams: a list of teams they are associated with (json)
        """
        player_id = player.get_player_id()
        params = {"player_id": player_id}
        response = requests.post(self.baseurl + "api/view/players/team_lookup",
                                 params=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def lookup_all_teams(self):
        params = {"year": get_this_year()}
        response = requests.post(self.baseurl + "api/view/teams",
                                 params=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def get_upcoming_games(self, player):
        """Returns league leaders for some stat

        Parameters:
            player: the player (Player)
        Returns:
            a list of upcoming games
        """
        player_id = player.get_player_id()
        params = {"player_id": player_id}
        response = requests.post(self.baseurl + "api/bot/upcoming_games",
                                 data=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def get_events(self):
        """Returns a dictionary object of the events
        """
        r = requests.get(self.baseurl +
                         "website/event/{}/json".format(date.today().year))
        if (r.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        return r.json()

    def league_leaders(self, stat):
        """Returns league leaders for some stat

        Parameters:
            stat: the stat classification (string)
        Returns:
            r.json(): a list of leaders
        """
        params = {"stat": stat, "year": date.today().year}
        r = requests.post(self.baseurl + "api/view/league_leaders",
                          data=params,
                          headers=self.headers)
        if (r.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        return r.json()

    def fun_meter(self):
        """Returns the amount of fun

        Returns:
            fun: an amount of fun (int)
        """
        params = {"year": date.today().year}
        r = requests.post(self.baseurl + "api/view/fun",
                          data=params,
                          headers=self.headers)
        if (r.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        return r.json()
