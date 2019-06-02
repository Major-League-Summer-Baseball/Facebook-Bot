'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Holds information and the message received by some sender
    Additionally holds some objects that are formatted upon sending a message
'''
from api.errors import OptionException, MessengerException
from copy import deepcopy


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
        return "{}: {} vs {} @ {} on {}".format(self._data['date'],
                                                self._data['home_team'],
                                                self._data['away_team'],
                                                self._data['time'],
                                                self._data['field'])


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


class Option():
    """
        Holds information about an option (payload, buttons, quick replies)
        title: the message title of the option
        data: the data object of the payload
            (needs to have format method or be a string)
    """

    def __init__(self, title, data):
        """Constructor"""
        self._title = title
        if isinstance(data, DataFormatter):
            self._data = data
        elif isinstance(data, str):
            self._data = StringFormatter(data)
        else:
            raise OptionException("Given non-formatted data or a string")

    def get_data(self):
        """Returns a data object that has a format method"""
        return self._data.format()

    def get_raw_data(self):
        """Return the raw data object that has not been formatted"""
        return self._data

    def get_title(self):
        """Returns the title of the option (str)"""
        return self._title


class Payload():
    """
        A message payload - used for quick replies and buttons
    """
    QUICK_REPLY_TYPE = "text"
    BUTTON_TYPE = "postback"

    def __init__(self, payload_type=None, options=[]):
        """Constructor"""
        if payload_type is not None:
            self._type = payload_type
            if not self.is_button_reply() and not self.is_quick_reply():
                raise MessengerException("Unsupported payload type")
        else:
            self._type = Payload.BUTTON_TYPE
        self._options = options

    def add_option(self, option):
        """Adds the given Option"""
        self._options.append(option)

    def is_quick_reply(self):
        """Is the payload a quick reply"""
        return self._type == Payload.QUICK_REPLY_TYPE

    def is_button_reply(self):
        """Is the payload a button reply"""
        return self._type == Payload.BUTTON_TYPE

    def get_options(self):
        """Returns a copy of the options"""
        return deepcopy(self._options)

    def get_payload_response(self):
        """Returns an array of payload responses"""
        payload = []
        for option in self._options:
            payload.append({"type": self._type,
                            "title": option.get_title(),
                            "payload": option.get_data()})
        return payload


class Message():
    """
        Holds information about the message that was received from messenger
        or information to send back using a messenger.
    """

    def __init__(self,
                 sender_id,
                 recipient_id=None,
                 message=None,
                 payload=None):
        """Constructor"""
        self._message = message
        self._payload = payload
        self._sender_id = sender_id
        self._recipient_id = recipient_id

    def get_sender_id(self):
        """Gets the the sender id"""
        return self._sender_id

    def get_message(self):
        """Gets the message string"""
        return self._message

    def get_payload(self):
        """Gets the payload of the message"""
        return self._payload

    def get_recipient_id(self):
        """Gets the recipient id"""
        return self._recipient_id

    def __str__(self):
        """Returns string of the message"""
        return "{}: {} from {}".format(self._sender_id,
                                       self._message,
                                       self._recipient_id)
