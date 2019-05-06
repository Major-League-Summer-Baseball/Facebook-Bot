'''
@author: Dallas Fraser
@author: 2019-04-29
@organization: MLSB
@project: Facebook Bot
@summary: Holds various actions of the Facebook bot
    An actions is a combination of various states
    that together form a coherent action that user can perform
    E.g. Submit a score, Subscribe to a team
    All actions should keep track of their own state
'''
from api.errors import ActionException


class ActionState():
    """Holds the state of the action"""

    def __init__(self, key=None, dictionary=None):
        # id needs to be set by a parameter or in the dictionary
        self.key = key
        if dictionary is not None:
            self.from_dictionary(dictionary)
        if self.key is None:
            raise ActionException("Action id not set")

    def from_dictionary(self, dictionary):
        """Loads action state from a dictionary"""
        self.key = (self.key if dictionary.get("id", None) is None
                    else dictionary.get("id"))

    def to_dictionary(self):
        """Return a dictionary representation of the action state"""
        return {"id": self.key}


class ActionInterface():
    """
    The action interface
    """

    def __init__(self, database, platform, messenger, message):
        """Constructor"""
        self.database = database
        self.platform = platform
        self.message = message
        self.messenger = messenger

    def process(self, action_map):
        """Process the action
        Parameters:
            action_map: maps action ids to their classes
        """
        raise NotImplementedError("Action needs to implement process method")
