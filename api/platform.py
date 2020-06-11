'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds an implementation of the interaction with the MLSB platform
'''
from typing import List, TypedDict
from datetime import date
from api.players.player import Player
from api.helper import get_this_year
from api.logging import LOGGER
from api.errors import PLATFORMMESSAGE, PlatformException, IdentityException,\
     NotCaptainForAnyTeam, TeamDoesNotExist, GameDoesNotExist,\
     NotCaptainException
import requests


class PlayerInfo(TypedDict):
    """The player info type from the platform."""
    player_id: int
    player_name: str
    gender: str
    active: bool
    ID = "player_id"
    NAME = "player_name"
    GENDER = "gender"
    ACTIVE = "active"
    FEMALE = "f"
    MALE = "m"


class Fun(TypedDict):
    """The fun object type from the platform."""
    year: int
    count: int
    YEAR = "year"
    count = "count"


class League(TypedDict):
    """A league of the platform."""
    league_id: int
    league_name: str
    ID = "league_id"
    NAME = "league_name"


class Division(TypedDict):
    """A division of the platform."""
    division_id: int
    division_name: str
    division_shortname: str
    ID = "division_id"
    NAME = "division_name"
    SHORT_NAME = "division_shortname"


class Sponsor(TypedDict):
    """A sponsor the platform and some team."""
    sponsor_id: int
    sponsor_name: str
    link: str
    description: str
    active: bool
    ID = "sponsor_id"
    NAME = "sponsor_name"
    DESCRIPTION = "description"
    ACTIVE = "active"


class Team(TypedDict):
    """The standard representation of a team on the platform."""
    team_id: int
    team_name: str
    captain: PlayerInfo
    sponsor_id: int
    league_id: int
    color: str
    year: int
    espys: float
    ID = "team_id"
    NAME = "team_name"
    CAPTAIN = "captain"
    COLOR = "color"
    YEAR = "year"
    ESPYS = "espys"
    SPONSOR_ID = Sponsor.ID
    LEAGUE_ID = League.ID


class TeamRoster(TypedDict):
    """A team roster of some team."""
    captain: PlayerInfo
    players: List[PlayerInfo]
    CAPTAIN = "captain"
    PLAYERS = "players"


class Game(TypedDict):
    """A game for some league between two teams."""
    home_team: str
    home_team_id: int
    away_team: str
    away_team_id: int
    date: str  # %YYYY-%MM-%DD
    time: str  # %H:%M
    league_id: int
    division_id: int
    game_id: int
    status: str
    field: str
    AWAY_TEAM = "away_team"
    AWAY_TEAM_ID = "away_team_id"
    HOME_TEAM = "home_team"
    HOME_TEAM_ID = "home_team_id"
    DATE = "date"
    TIME = "time"
    ID = "game_id"
    STATUS = "status"
    FIELD = "field"
    LEAGUE_ID = League.ID
    DIVISION_ID = Division.ID


class GameSheet(TypedDict):
    """A game sheet to submit for a game."""
    game_id: int
    player_id: int
    score: int
    hr: List[int]
    ss: List[int]
    GAME_ID = Game.ID
    PLAYER_ID = PlayerInfo.ID
    SCORE = "score"
    HR = "hr"
    SS = "ss"


class PlatformService():

    def __init__(self, headers: dict, baseurl: str):
        """A Service for interacting with MLSB platform.

        Args:
            headers (dict): containers admin name and password
            baseurl (str): the URL of the platform
        """
        self.headers = headers
        self.baseurl = baseurl

    def lookup_player_by_name(self, name: str) -> PlayerInfo:
        """Lookup the player by name

        Args:
            name (str): the name to lookup

        Raises:
            PlatformException: Unable to communicate with platform

        Returns:
            PlayerInfo: the one player associated with the name otherwise None
        """
        submission = {PlayerInfo.NAME: name,  PlayerInfo.ACTIVE: 1}
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

    def lookup_player_by_email(self, email: str) -> PlayerInfo:
        """Lookup the player associated with the email.

        Args:
            email (str): the email

        Raises:
            PlatformException: unable to communicate with platform
            IdentityException: no player identified

        Returns:
            PlayerInfo: the player associated with platform
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

    def lookup_teams_player_associated_with(self,
                                            player: Player) -> List[Team]:
        """Lookup all the teams a given player is associated with.

        Args:
            player (Player): the player

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            List[Team]: the associated teams
        """
        player_id = player.get_player_id()
        params = {PlayerInfo.ID: player_id}
        response = requests.post(self.baseurl + "api/view/players/team_lookup",
                                 params=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def lookup_all_teams(self) -> dict:
        """Lookup all the teams from this year.

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            dict: a map from team ids to their team
        """
        params = {Team.YEAR: get_this_year()}
        response = requests.post(self.baseurl + "api/view/teams",
                                 params=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def get_upcoming_games(self, player: Player) -> List[Game]:
        """Get the upcoming games for the given player.

        Args:
            player (Player): the player

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            List[Game]: a list of upcoming games
        """
        player_id = player.get_player_id()
        params = {PlayerInfo.ID: player_id}
        response = requests.post(self.baseurl + "api/bot/upcoming_games",
                                 data=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.critical("Unable to contact the MLSB platform")
            LOGGER.error(str(response.json()))
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def get_events(self) -> dict:
        """Returns a map of event names to their date

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            dict: map of event name to event
        """
        request_sub_url = "website/event/{}/json".format(date.today().year)
        response = requests.get(self.baseurl + request_sub_url)
        if (response.status_code != 200):
            LOGGER.error(str(response.json()))
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def league_leaders(self, stat: str) -> List[PlayerInfo]:
        """Returns a list of league leaders for given stat

        Args:
            stat (str): the stat to measure by

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            List[PlayerInfo]: a list of players sort by stat
        """
        params = {"stat": stat, Team.YEAR: date.today().year}
        response = requests.post(self.baseurl + "api/view/league_leaders",
                                 data=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.error(str(response.json()))
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def fun_meter(self) -> List[Fun]:
        """Returns the fun amount for this year

        Raises:
            PlatformException: unable to communicate with platform

        Returns:
            List[Fun]: a list with amount of fun this year otherwise empty
        """
        params = {Team.YEAR: date.today().year}
        response = requests.post(self.baseurl + "api/view/fun",
                                 data=params,
                                 headers=self.headers)
        if (response.status_code != 200):
            LOGGER.error(str(response.json()))
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def games_to_submit_scores_for(self, player_id: int,
                                   team_id: int) -> List[Game]:
        """Returns a list of games the player can submit for the given team.

        Args:
            player_id (int): the id of the player
            team_id (int): the id of the team

        Raises:
            NotCaptainForAnyTeam: given player not captain of team
            TeamDoesNotExist: given team does not exist
            PlatformException: unable to communicate with platform

        Returns:
            List[Game]: a list of games
        """
        params = {PlayerInfo.ID: player_id, "team": team_id}
        response = requests.post(self.baseurl + "api/bot/captain/games",
                                 data=params,
                                 headers=self.headers)
        if response.status_code == 401:
            raise NotCaptainForAnyTeam(
                "Says you are not a captain, check admin")
        elif response.status_code == 404:
            raise TeamDoesNotExist("Teams does not seem to exist")
        elif (response.status_code != 200):
            raise PlatformException(PLATFORMMESSAGE)
        games = response.json()
        return games

    def lookup_team_roster(self, team_id: int) -> TeamRoster:
        """Lookup the team roster for the given team

        Args:
            team_id (int): the id of the team to lookup

        Raises:
            TeamDoesNotExist: the given team does not exist
            PlatformException: unable to communicate with platform

        Returns:
            TeamRoster: the team roster
        """
        request_url = self.baseurl + "/api/teamroster/" + str(team_id)
        response = requests.get(request_url)
        if response.status_code == 400:
            raise TeamDoesNotExist("Teams does not seem to exist")
        if response.status_code != 200:
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()

    def submit_game_sheet(self, game_sheet: GameSheet) -> bool:
        """Submit a game sheet

        Args:
            game_sheet (GameSheet): the game sheet to submit

        Raises:
            GameDoesNotExist: the game does not exist
            NotCaptainException: the player submitting sheet is not a captain
            PlatformException: unable to communicate with platform

        Returns:
            bool: True if successful otherwise False
        """
        request_url = self.baseurl + "/api/bot/submit_score"
        response = requests.post(request_url,
                                 data=game_sheet, headers=self.headers)
        if response.status_code == 404:
            raise GameDoesNotExist("Game does not exist")
        elif response.status_code == 401:
            raise NotCaptainException("The player not a captain of team")
        elif response.status_code != 200:
            raise PlatformException(PLATFORMMESSAGE)
        return response.json()
