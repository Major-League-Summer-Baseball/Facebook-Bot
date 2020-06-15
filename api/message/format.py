'''
@author: Dallas Fraser
@author: 2020-06-14
@organization: MLSB
@project: Facebook Bot
@summary: Holds formatter of various types
'''
from api.mlsb.typing import Game

class DataFormatter():
    """
        The data formatter interface
    """

    def __init__(self, data):
        """Constructor"""
        self._data = data

    def format(self):
        """Returns a formatted string of the data"""
        raise NotImplementedError("Need to implement the format of data")

    def __str__(self):
        return str(self._data)


class EventFormatter(DataFormatter):
    """
        Formatter used for events json
    """

    def format(self):
        """Returns a formatted string of the event"""
        return "{} - {}".format(self._data['event'].replace("_", " "),
                                self._data['date'])


class GameFormatter(DataFormatter):
    """
        Formatter used for game json
    """

    def format(self):
        """Returns a formatted string representation of the game"""
        return "{}:\n{} vs {}\n @ {} on {}".format(self._data[Game.DATE],
                                                   self._data[Game.HOME_TEAM],
                                                   self._data[Game.AWAY_TEAM],
                                                   self._data[Game.TIME],
                                                   self._data[Game.FIELD])


class LeagueLeaderFormatter(DataFormatter):
    """
        Formatter used for league leader json
    """

    def format(self):
        """Returns a formatted string representation of the league leader"""
        return "{} ({}): {:d}".format(self._data['name'],
                                      self._data['team'],
                                      self._data['hits'])


class StringFormatter(DataFormatter):
    """
        Formatter used for a normal string
    """

    def format(self):
        """Returns a formatted string representation of the data"""
        return str(self._data)
