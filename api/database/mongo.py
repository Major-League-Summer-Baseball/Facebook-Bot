'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds an implementation of the the database service
'''
from api.players.player import Player


class DatabaseService():
    """Database service that uses mongo as the underlying implementation"""

    def __init__(self, mongo):
        self.mongo = mongo

    def get_player(self, facebook_id):
        """Returns the user object for the given facebook id"""
        return self.mongo.db.users.find_one({'facebook_id': facebook_id})

    def create_player(self, sender_id, name):
        """Creates a user with the given sender_id and given name"""
        player = Player(messenger_id=sender_id, messenger_name=name)
        self.mongo.db.users.insert(player)
        return player

    def save_player(self, user):
        self.mongo.db.users.save(user)

    def already_in_league(self, player):
        """Check if a player already in the league

        Parameters:
            player: the player object (MLSB Player)
        Returns:
            taken: True if someone already taken that player, False otherwise
        TODO:
            Currently this method will limit a user to only using one messenger
        """
        taken = True
        user = self.mongo.db.users.find_one({'player_id': player['player_id']})
        if user is None:
            taken = False
        return taken
