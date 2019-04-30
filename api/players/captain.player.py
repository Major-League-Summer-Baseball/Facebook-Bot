'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: The captain of a team
'''
from api.players.player import Player


class Captain(Player):
    IDENTIFIER = "Captain"

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
        return self.team_captain is not None and self.team_captain == team_id
