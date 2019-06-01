'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: A double for the platform used for testing (stubs the platform APIs)
'''
from api.errors import IdentityException


class PlatformDouble():
    """Stub the platform calls"""

    def __init__(self, player_by_email=None, player_by_name=None, teams=[]):
        """Constructor"""
        self.player_by_email = player_by_email
        self.player_by_name = player_by_name
        self.teams = teams

    def set_mock_player(self, player_by_email=None, player_by_name=None):
        """Set the mock player the platform should return upon lookups"""
        if player_by_email is not None:
            self.player_by_email = player_by_email
        if player_by_name is not None:
            self.player_by_name = player_by_name

    def set_mock_teams(self, teams=[]):
        """Sets the mock teams to return"""
        self.teams = teams

    def lookup_player_by_name(self, name):
        """Mmethod that just returns mock player"""
        return self.player_by_name

    def lookup_player_by_email(self, email):
        """Method that just returns mock player"""
        if self.player_by_email is None:
            raise IdentityException("Not sure who you are, ask admin")
        return self.player_by_email

    def lookup_all_teams(self):
        """Method that just returns mock team list"""
        team_dict = {}
        for team in self.teams:
            team_dict[team["team_id"]] = {}
        return team_dict

    def lookup_teams_player_associated_with(self, player):
        """Method that just returns mock team list"""
        return self.teams

    def set_mock_league_leaders(self, leaders):
        """Set the mock league leaders that are to be returned"""
        self._leaders = leaders

    def league_leaders(self, stat):
        """Method that just returns the mock league leaders"""
        return self._leaders

    def set_mock_fun_meter(self, fun_meter):
        """Set the mock fun meter that is to be returned"""
        self._fun_meter = fun_meter

    def fun_meter(self):
        """Method that just returns the mock fun meter"""
        return self._fun_meter

    def set_mock_events(self, events):
        """Set the mock events that are to be returned"""
        self._events = events

    def get_events(self):
        """Method that just returns the mock events"""
        return self._events

    def set_mock_upcoming_games(self, upcoming_games):
        """Set the mock upcoming games that are to be returned"""
        self._upcoming_games = upcoming_games

    def get_upcoming_games(self, player):
        """Method that just returns the mock upcoming games"""
        return self._upcoming_games
