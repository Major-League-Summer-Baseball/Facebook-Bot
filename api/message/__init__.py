'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Holds information and the message received by some sender
    Additionally holds some objects that are formatted upon sending a message
'''


class FormattedData():
    """Formatted data"""

    def __init__(self, data):
        """Constructor"""
        self._data = data

    def format(self):
        """Returns a formatted string of the data"""
        raise NotImplementedError("Need to implement the format of data")


class Event(FormattedData):
    """Event data"""

    def format(self):
        """Returns a formatted string of the event"""
        return "{} - {}".format(self._data['event'].replace("_", " "),
                                self._data['date'])


class Game(FormattedData):
    """Game data"""

    def format(self):
        """Returns a formatted string representation of the game"""
        return "{}: {} vs {} @ {} on {}".format(self._data['date'],
                                                self._data['home_team'],
                                                self._data['away_team'],
                                                self._data['time'],
                                                self._data['field'])


class LeagueLeader(FormattedData):
    """League leader data"""

    def format(self):
        """Returns a formatted string representation of the league leader"""
        return "{} ({}): {:d}".format(self._data['name'],
                                      self._data['team'],
                                      self._data['hits'])


class Option():
    """
        Holds information about an option (payload, buttons, quick replies)
        title: the message title of the option
        data: the data object of the payload (needs to have format method)
    """

    def __init__(self, title, data):
        """Constructor"""
        self._title = title
        self._data = data

    def get_data(self):
        """Returns a data object that has a format method"""
        return self._data

    def get_title(self):
        """Returns the title of the option (str)"""
        return self._title


class Message():
    """
        Holds information about the message that was sent
    """

    def __init__(self, sender_id, message=None, payload=None):
        """Constructor"""
        self._message = message
        self._payload = payload
        self._sender_id = sender_id

    def get_sender_id(self):
        """Gets the the sender id"""
        return self._sender_id

    def get_message(self):
        """Gets the message string"""
        return self._message

    def get_payload(self):
        """Gets the payload of the message"""
        return self._payload
