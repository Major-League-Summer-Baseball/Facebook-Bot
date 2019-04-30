'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: The basic player
'''
from api.players.subscription import Subscription


class Player():
    IDENTIFIER = "Player"

    def __init__(self, dictionary=None):
        if dictionary is not None:
            self.from_dictionary(dictionary)

    def from_dictionary(self, dictionary):
        """Sets the player attributes from the given dictionary"""
        self.player = dictionary["player"]
        self.teams = dictionary["teams"]
        self.subscription = Subscription(dictionary['subscription'])

    def to_dictionary(self):
        """Returns the dictionarty representation of the player"""
        return {"player": self.player,
                "teams": self.teams,
                "subscription": self.subscription.to_dictionary()}

    def is_captain(self):
        """Returns whether the given player is a captain"""
        return False

    def is_convenor(self):
        """Returns whether the given player is a convenor"""
        return False

    def get_subscription(self):
        """Returns the what the player is subscribed to"""
        return self.subscription

    def set_subscription(self, subscription):
        """Setter for the subscription"""
        self.subscription = subscription
