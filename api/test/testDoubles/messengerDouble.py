'''
@author: Dallas Fraser
@author: 2019-05-31
@organization: MLSB
@project: Facebook Bot
@summary: A double for the messenger
'''
from api.messenger.user import User
from api.message import Message
from api.test.testDoubles.errors import TestDoubleException


class MessengerDouble():
    """Stub a messenger so one can view what was sent"""

    def __init__(self, user=None):
        """Constructor"""
        if user is None or isinstance(user, User):
            self.user = user
        else:
            raise TestDoubleException("Illegal mock user")
        self.messages = []

    def send_message(self, message):
        """Just store the message so can view it for testing"""
        self.messages.append(message)

    def get_messages(self):
        """Returns the list of messages sent"""
        return self.messages

    def clear_messages(self):
        """Clears all the messages sent"""
        self.messages = []

    def parse_response(self, response):
        """Do not think this will be needed for testing"""
        self.response = response
        sender_id = "test_id"
        if self.user is not None:
            sender_id = self.user.get_sender_id()
        message = Message(sender_id, response)
        return message

    def set_mock_user(self, user):
        """Set the mock user to lookup"""
        if isinstance(user, User):
            self.user = user
        else:
            raise TestDoubleException("Illegal mock user")

    def lookup_user_id(self, messenger_id):
        """Return the mock user object"""
        return self.user
