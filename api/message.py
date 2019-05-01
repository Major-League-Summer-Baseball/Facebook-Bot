'''
@author: Dallas Fraser
@author: 2019-08-27
@organization: MLSB
@project: Facebook Bot
@summary: Holds information and the message received by some sender
'''


class Option():
    """
        Holds information about an option (payload, buttons, quick replies)
    """

    def __init__(self, title, data):
        """Constructor"""
        self._title = title
        self._data = data

    def get_data(self):
        """A data object that has a method format"""
        return self._data

    def get_title(self):
        return self._title


class Message():
    """
        Holds information about the message that was sent
    """

    def __init__(self, sender_id,
                 receipent_id=None,
                 message=None,
                 payload=None):
        """Constructor"""
        self._message = message
        self._payload = payload
        self._sender_id = sender_id

    def get_sender_id(self):
        """Gets the the sender id"""
        return self._sender_id

    def get_recepient_id(self):
        """Get the person who received the message"""
        return self._recepient_id

    def get_message(self):
        """Gets the message string"""
        return self._message

    def get_payload(self):
        """Gets the payload of the message"""
        return self._payload
