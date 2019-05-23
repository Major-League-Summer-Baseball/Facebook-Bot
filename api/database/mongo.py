'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds an implementation of the the database service
'''
from api.logging import LOGGER
from api.errors import DatabaseException
from api.players.player import Player


class DatabaseService():
    """Database service that uses mongo as the underlying implementation"""

    def __init__(self, mongo):
        self.mongo = mongo

    def get_player(self, messenger_id):
        """Returns the user object for the given messenger id"""
        search_parameters = Player.get_messenger_search(messenger_id)
        player_dictionary = self.mongo.db.users.find_one(search_parameters)
        if player_dictionary is None:
            return None
        return Player(dictionary=player_dictionary)

    def create_player(self, sender_id, name):
        """Creates a user with the given sender_id and given name"""
        player = Player(messenger_id=sender_id, name=name)
        self.mongo.db.users.insert(player.to_dictionary())
        return player

    def save_player(self, player):
        if player is None:
            raise DatabaseException("Saving: a non-existent user (None)")
        elif not isinstance(player, Player):
            raise DatabaseException("Saving: player of the wrong type")
        search_parameters = player.messenger_search()
        player_dictionary = self.mongo.db.users.find_one(search_parameters)
        if player_dictionary is None:
            player_dictionary = player.to_dictionary()
        else:
            temp = player.to_dictionary()
            temp["_id"] = player_dictionary["_id"]
            player_dictionary = temp
        self.mongo.db.users.save(player_dictionary)

    def already_in_league(self, player_info):
        """Check if a player already in the league

        Parameters:
            player_info: the player infor from the platform (dictionary)
        Returns:
            taken: True if someone already taken that player, False otherwise
        TODO:
            Currently this method will limit a user to only using one messenger
        """
        taken = True
        search_parameters = Player.get_player_search(player_info)
        user = self.mongo.db.users.find_one(search_parameters)
        if user is None:
            taken = False
        return taken
