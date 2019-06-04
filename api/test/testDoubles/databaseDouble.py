'''
@author: Dallas Fraser
@author: 2019-05-31
@organization: MLSB
@project: Facebook Bot
@summary: A double for the database interaction
'''
from api.players.player import Player


class DatabaseDouble():
    """Class that stubs mongo for testing database interaction"""

    def __init__(self, player=None, already_in_league=False, convenors=[]):
        """Constructor"""
        self.created_player = None
        self.player = player
        self.saved_player = None
        self._already_in_league = already_in_league
        self._convenors = []

    def save_player(self, player):
        """Stub for the save player"""
        self.saved_player = player

    def inspect_saved_player(self):
        """Returns what player object was saved using save player"""
        return self.saved_player

    def set_player(self, player):
        """Helper to set the player to that will be returned"""
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

    def set_convenors(self, convenors):
        """Sets the mock of the convenors"""
        self._convenors = convenors

    def get_convenor_name_list(self):
        """Returns a list of mocked convenors"""
        return self._convenors
