'''
@author: Dallas Fraser
@author: 2020-06-15
@organization: MLSB
@project: Facebook Bot
@summary: Holds the various types of objects from the MLSB platform
'''
from typing import List, TypedDict


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
