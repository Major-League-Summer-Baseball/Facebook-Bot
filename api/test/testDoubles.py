'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Test doubles for various objects that are used for testing
'''
from api.actions import ActionInterface
from api.players.player import Player
from api.messenger.user import User
from api.message import Message
from api.errors import IdentityException


class NoAction(ActionInterface):
    """Stub for the next action to allow testing individual actions"""

    def process(self, action_map):
        return


class TestDoubleException(Exception):
    """Exceptions raised by on the test doubles"""
    pass


class MessengerStub():
    """Stub a messenger so one can view what was sent"""

    def __init__(self, user=None):
        """Constructor"""
        if user is None or isinstance(user, User):
            self.user = user
        else:
            raise TestDoubleException("Illegal mock user")
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
        else:
            raise TestDoubleException("Illegal mock user")

    def lookup_user_id(self, messenger_id):
        """Return the mock user object"""
        return self.user

    def get_convenor_email_list(self):
        return


class PlatformStub():
    """Stub the platform calls"""

    def __init__(self, player_by_email=None, player_by_name=None):
        """Constructor"""
        self.player_by_email = player_by_email
        self.player_by_name = player_by_name

    def set_mock_player(self, player_by_email=None, player_by_name=None):
        """Set the mock player the platform should return upon lookups"""
        if player_by_email is not None:
            self.player_by_email = player_by_email
        if player_by_name is not None:
            self.player_by_name = player_by_name

    def lookup_player_by_name(self, name):
        """Mock method that just returns mock player"""
        return self.player_by_name

    def lookup_player_by_email(self, email):
        """Mock method that just returns mock player"""
        if self.player_by_email is None:
            raise IdentityException("Not sure who you are, ask admin")
        return self.player_by_email


class MongoStub():
    """Class that stubs mongo for testing database interaction"""

    def __init__(self, player=None, already_in_league=False):
        """Constructor"""
        self.created_player = None
        self.player = player
        self.saved_player = None
        self._already_in_league = already_in_league

    def save_player(self, player):
        """Stub for the save player"""
        self.saved_player = player

    def inspect_saved_player(self):
        """Returns what player object was saved using save player"""
        return self.saved_player

    def set_player(self, player):
        """Helper for set the player to return"""
        self.player = player

    def get_player(self, messenger_id):
        """Stub for the get player"""
        return self.player

    def already_in_league(self, player_info):
        """Stub for whether the player is already in the league or not"""
        return self._already_in_league

    def set_already_in_league(self, already_in_league):
        """Set what to return for already in the league"""
        self._already_in_league = already_in_league

    def create_player(self, sender_id, name):
        self.created_player = Player(messenger_id=sender_id,
                                     name=name)
        return self.created_player
