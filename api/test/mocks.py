'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Mocks for various objects that are used for teting
'''
from api.messenger.user import User
from api.message import Message
from api.errors import IdentityException


class MockException(Exception):
    pass


class MockMessenger():
    """Mocks a messenger so one can view what was sent"""

    def __init__(self, user=None):
        """Constructor"""
        if user is None or isinstance(user, User):
            self.user = user
        else:
            raise MockException("Illegal mock user")
        self.message = None

    def send_message(self, message):
        """Just store the message so can view it for testing"""
        self.message = message

    def get_message(self):
        """Get the message back later"""
        return self.message

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
        raise MockException("Illegal mock user")

    def lookup_user_id(self):
        """Return the mock user object"""
        return self.user


class MockPlatform():
    """Mocks the platform calls"""

    def __init__(self, player=None):
        """Constructor"""
        self.player = player

    def set_mock_player(self, player):
        """Set the mock player the platform should return upon lookups"""
        self.player = player

    def lookup_player(self, name):
        """Mock method that just returns mock player"""
        return self.player

    def lookup_player_email(self, email):
        """Mock method that just returns mock player"""
        if self.player is None:
            raise IdentityException("Not sure who you are, ask admin")
        return self.player


class MockDatabase():
    def __init__():
        pass
