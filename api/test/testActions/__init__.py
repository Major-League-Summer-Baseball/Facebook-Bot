'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds a base class that setups some common things needed
'''
from api.test.testDoubles.messengerDouble import MessengerDouble
from api.test.testDoubles.databaseDouble import DatabaseDouble
from api.test.testDoubles.platformDouble import PlatformDouble
from api.helper import get_this_year
from random import randint, choice
from datetime import datetime
import unittest
import string


class TestActionBase(unittest.TestCase):
    """Base Test Action"""
    RANDOM_ID_UPPER_RANGE = 10000
    RANDOM_ESPY_RANGE = 1000000

    def setUp(self):
        """Setups all the test doubles"""
        self.db = DatabaseDouble()
        self.platform = PlatformDouble()
        self.messenger = MessengerDouble()
        self.random_ids = []

    def create_action(self, action_class):
        """Will commonly need to create actions"""
        return action_class(self.db,
                            self.platform,
                            self.messenger)

    def random_player(self):
        """Return a random player"""
        return {"player_id": self.random_id(),
                "player_name": self.random_string(),
                "gender": self.random_gender(),
                "active": True}

    def random_team(self, captain=None, year=get_this_year()):
        """Return a random team

        Parameters:
            captain: the player who is to be captain (default: random player)
            year: the year of the team (default: current year)
        """
        captain = captain if captain is not None else self.random_player()
        return {"team_id": self.random_id(),
                "team_name": self.random_string(),
                "captain": captain,
                "sponsor_id": self.random_id(),
                "color": self.random_string(),
                "year": year,
                "espys": self.random_number()}

    def random_game(self, team_one, team_two, date=None):
        """Return a random game between the two teams"""
        return {"home_team": team_one.get("team_name", self.random_string()),
                "home_team_id": team_one.get("team_id", self.random_id()),
                "away_team": team_two.get("team_name", self.random_string()),
                "away_team_id": team_two.get("team_id", self.random_id()),
                "date": date if date is not None else self.random_date(),
                "time": "8:00",
                "league_id": 1,
                "game_id": self.random_id(),
                "status": self.random_string(),
                "field": "WP1"}

    def random_roster(self, team, captain=None):
        """Return a random roster"""
        captain = captain if captain is not None else self.random_player()
        players = [captain]
        for i in range(randint(1, 3)):
            players.append(self.random_player())
        return {"team_id": team, "captain": captain, "players": players}

    def random_date(self):
        return (datetime.today() +
                datetime.timedelta(days=randint(-10, 10))).strftime("%Y-%m-%d")

    def random_gender(self):
        """Returns a random gender"""
        return "m" if randint(0, 1) == 0 else "f"

    def random_id(self):
        """Returns a random id"""
        i = randint(0, TestActionBase.RANDOM_ID_UPPER_RANGE)
        while i in self.random_ids:
            i = randint(0, TestActionBase.RANDOM_ID_UPPER_RANGE)
        self.random_ids.append(i)
        return i

    def random_number(self):
        """Returns a random number"""
        return randint(0, TestActionBase.RANDOM_ESPY_RANGE)

    def random_string(self, stringLength=10):
        """Returns a random string"""
        letters = string.ascii_lowercase
        return ''.join(choice(letters) for i in range(stringLength))
