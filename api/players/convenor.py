'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The convenor of a league
'''
from api.players.captain import Captain


class Convenor(Captain):
    IDENTIFIER = "Convenor"

    def __init__(self, dictionary=None):
        if dictionary is not None:
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        super().from_dictionary(self, dictionary)
        self.teamroster = dictionary["teamroster"]
        self.team_captain = dictionary["team_captain"]

    def to_dictionary(self):
        """Returns the dictionarty representation of the player"""
        base = super().to_dictionary(self)
        base["teamroster"] = self.teamroster
        base["team_captain"] = self.team_captain
        return base

    def is_captain(self, team_id):
        """Returns whether the given player is a captain of the given team"""
        return True

    def is_convenor(self):
        return True
